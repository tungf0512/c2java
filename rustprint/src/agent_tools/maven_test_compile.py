"""Tool to run Maven test compilation on a translated Java repo."""

from __future__ import annotations

import logging
import os
import subprocess
from pathlib import Path
from typing import Any, Optional

try:
    from pydantic_ai import RunContext, Tool
except ImportError:  # pragma: no cover - lets parser unit tests run without optional app deps.
    RunContext = Any

    class Tool:  # type: ignore[no-redef]
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            self.args = args
            self.kwargs = kwargs

try:
    from .maven_compile import (
        _get_target_repo_path,
        _resolve_working_dir,
        filter_maven_compile_errors,
    )
except ImportError:  # pragma: no cover - direct file import in unit tests.
    from maven_compile import (  # type: ignore[no-redef]
        _get_target_repo_path,
        _resolve_working_dir,
        filter_maven_compile_errors,
    )

logger = logging.getLogger(__name__)


def filter_maven_test_compile_errors(raw_output: str, workspace_root: Optional[Path | str] = None) -> str:
    """Extract actionable test-compilation diagnostics from Maven output."""

    return filter_maven_compile_errors(raw_output, workspace_root=workspace_root)


def _find_nearest_pom(start: Path, workspace_root: Path) -> Optional[Path]:
    current = start.resolve()
    root = workspace_root.resolve()
    for _ in range(30):
        if (current / "pom.xml").is_file():
            return current
        if current == root:
            break
        parent = current.parent
        if parent == current:
            break
        current = parent
    if (root / "pom.xml").is_file():
        return root
    return None


def _build_maven_command(
    workspace_root: Path,
    requested_dir: Path,
    goals: list[str],
) -> tuple[Path, list[str], Optional[str]]:
    """Return cwd, command, and optional Maven module path."""

    workspace_root = workspace_root.resolve()
    requested_dir = requested_dir.resolve()
    project_dir = _find_nearest_pom(requested_dir, workspace_root)
    if project_dir is None:
        raise FileNotFoundError(f"No pom.xml found at or above {requested_dir}.")

    root_has_pom = (workspace_root / "pom.xml").is_file()
    if root_has_pom and project_dir != workspace_root:
        module_path = str(project_dir.relative_to(workspace_root)).replace("\\", "/")
        return workspace_root, ["mvn", "-q", "-pl", module_path, "-am", *goals], module_path

    return project_dir, ["mvn", "-q", *goals], None


async def maven_test_compile(
    ctx: RunContext[Any],
    working_dir: Optional[str] = None,
    timeout_seconds: int = 300,
) -> str:
    """Run `mvn -q -DskipTests test-compile` for a Java Maven project.

    If working_dir points inside a Maven module under an aggregator root, the
    command runs from the root with `-pl <module> -am`.
    """

    deps = ctx.deps
    repo_path = _get_target_repo_path(deps)
    if not repo_path:
        return "Error: No Java repository path in deps."

    workspace_root = Path(repo_path).resolve()
    if not workspace_root.is_dir():
        return f"Error: Java repo path is not a directory: {workspace_root}"

    try:
        requested_dir = _resolve_working_dir(workspace_root, working_dir)
        cwd, cmd, module_path = _build_maven_command(
            workspace_root,
            requested_dir,
            ["-DskipTests", "-Dstyle.color=never", "test-compile"],
        )
    except (ValueError, FileNotFoundError) as exc:
        return f"Error: {exc}"

    timeout_seconds = max(1, min(int(timeout_seconds), 900))
    env = {**os.environ, "MAVEN_OPTS": os.environ.get("MAVEN_OPTS", "")}

    logger.info("=" * 80)
    logger.info("TOOL CALL: maven_test_compile")
    logger.info("  Workspace   : %s", workspace_root)
    logger.info("  Working dir : %s", working_dir or "(workspace root)")
    logger.info("  Module      : %s", module_path or "(none)")
    logger.info("  CWD         : %s", cwd)
    logger.info("  Command     : cd %s && %s", cwd, " ".join(cmd))
    logger.info("=" * 80)

    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            env=env,
        )
    except subprocess.TimeoutExpired:
        logger.warning("[maven_test_compile] timeout (%ss)", timeout_seconds)
        return (
            f"Error: Maven test compilation timed out after {timeout_seconds} seconds. "
            "Try narrowing the working_dir or simplifying the generated tests."
        )
    except FileNotFoundError:
        logger.warning("[maven_test_compile] mvn not found")
        return "Error: 'mvn' command not found. Ensure Maven is installed and on PATH."
    except Exception as exc:
        logger.exception("[maven_test_compile] subprocess error: %s", exc)
        return f"Error running Maven test compilation: {exc}"

    stdout = result.stdout or ""
    stderr = result.stderr or ""
    raw_output = f"{stdout}\n{stderr}"
    logger.info(
        "[maven_test_compile] exit_code=%s stdout:\n%s\nstderr:\n%s",
        result.returncode,
        stdout,
        stderr,
    )

    if result.returncode != 0:
        attempts = getattr(deps, "maven_test_compile_attempts", 0) + 1
        setattr(deps, "maven_test_compile_attempts", attempts)
        filtered = filter_maven_test_compile_errors(raw_output, workspace_root=workspace_root)
        if not filtered:
            filtered = "(Maven test-compile failed, but no javac diagnostics were found. Check test dependencies or pom.xml.)"
        return (
            f"Still has Maven test-compilation errors. Iteration {attempts}.\n\n"
            "Fix the Java test code or Maven configuration according to the errors below, then call maven_test_compile again.\n\n"
            "<MAVEN_TEST_COMPILE_ERRORS>\n"
            f"{filtered}\n"
            "</MAVEN_TEST_COMPILE_ERRORS>"
        )

    setattr(deps, "maven_test_compile_attempts", 0)
    logger.info("[maven_test_compile] Done. Maven test-compile passed (exit 0).")
    return "Done. Maven test-compile passed. Proceed to the next step."


maven_test_compile_tool = Tool(
    function=maven_test_compile,
    name="maven_test_compile",
    description=(
        "Run `mvn -q -DskipTests test-compile` in the translated Java Maven project. "
        "If working_dir is inside a Maven module, the tool runs from the root with `-pl <module> -am`. "
        "If test compilation fails, it returns filtered actionable javac diagnostics only."
    ),
    takes_ctx=True,
)
