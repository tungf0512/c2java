"""Tool to run Maven compilation on a translated Java repo.

The agent should see only actionable compiler diagnostics, while full Maven
stdout/stderr remains available in logs for debugging.
"""

from __future__ import annotations

import logging
import os
import re
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

logger = logging.getLogger(__name__)

ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
ERROR_PREFIX_RE = re.compile(r"^\s*(?:\[ERROR\]\s*)?")
MAVEN_JAVA_DIAGNOSTIC_RE = re.compile(
    r"(?P<file>(?:[A-Za-z]:[\\/]|/|\.{1,2}[\\/]|[\w.-]+[\\/])[^:\n]*?\.java)"
    r":\[(?P<line>\d+)(?:,(?P<column>\d+))?\]\s*(?P<message>.*)"
)
MAVEN_NOISE_RE = re.compile(
    r"^(?:"
    r"COMPILATION ERROR|"
    r"BUILD FAILURE|"
    r"BUILD SUCCESS|"
    r"Total time:|"
    r"Finished at:|"
    r"Failed to execute goal|"
    r"To see the full stack trace|"
    r"Re-run Maven|"
    r"For more information|"
    r"\[Help \d+\]|"
    r"-> \[Help \d+\]"
    r")",
    re.IGNORECASE,
)


def _strip_ansi(text: str) -> str:
    return ANSI_RE.sub("", text or "")


def _strip_error_prefix(line: str) -> str:
    return ERROR_PREFIX_RE.sub("", line).rstrip()


def _relativize_path(path_text: str, workspace_root: Optional[Path]) -> str:
    path = Path(path_text)
    if workspace_root is not None:
        try:
            return str(path.resolve().relative_to(workspace_root.resolve()))
        except Exception:
            pass
    return path_text.replace("\\", "/")


def _is_continuation_line(line: str) -> bool:
    stripped = _strip_error_prefix(line).strip()
    if not stripped:
        return False
    if MAVEN_JAVA_DIAGNOSTIC_RE.search(stripped):
        return False
    if MAVEN_NOISE_RE.search(stripped):
        return False
    return line.lstrip().startswith("[ERROR]") and (
        stripped.startswith("symbol:")
        or stripped.startswith("location:")
        or stripped.startswith("^")
        or stripped.startswith("required:")
        or stripped.startswith("found:")
        or stripped.startswith("reason:")
        or stripped.startswith("method ")
        or stripped.startswith("constructor ")
        or stripped.startswith("class ")
        or stripped.startswith("interface ")
        or stripped.startswith("enum ")
        or stripped.startswith("package ")
        or stripped.startswith("cannot ")
        or stripped.startswith("incompatible ")
        or stripped.startswith("no suitable ")
        or stripped.startswith("reference to ")
        or stripped.startswith("bad operand")
        or stripped.startswith("unreported exception")
    )


def filter_maven_compile_errors(raw_output: str, workspace_root: Optional[Path | str] = None) -> str:
    """Extract actionable Java compiler diagnostics from noisy Maven output.

    Maven often wraps javac errors with plugin stack traces and help text. This
    function keeps file/line/column diagnostics plus their immediate javac detail
    lines, and drops lifecycle noise.
    """

    root = Path(workspace_root).resolve() if workspace_root is not None else None
    lines = _strip_ansi(raw_output).replace("\r\n", "\n").replace("\r", "\n").splitlines()

    diagnostics: list[str] = []
    seen_headers: set[str] = set()
    i = 0
    while i < len(lines):
        line = lines[i]
        clean = _strip_error_prefix(line).strip()
        match = MAVEN_JAVA_DIAGNOSTIC_RE.search(clean)
        if not match:
            i += 1
            continue

        rel_file = _relativize_path(match.group("file"), root)
        line_no = match.group("line")
        col_no = match.group("column")
        location = f"{rel_file}:[{line_no},{col_no}]" if col_no else f"{rel_file}:[{line_no}]"
        message = (match.group("message") or "").strip()
        header = f"{location} {message}".rstrip()

        block = [header]
        i += 1
        while i < len(lines) and _is_continuation_line(lines[i]):
            detail = _strip_error_prefix(lines[i]).strip()
            if detail:
                block.append(f"  {detail}")
            i += 1

        rendered = "\n".join(block)
        if header not in seen_headers:
            diagnostics.append(rendered)
            seen_headers.add(header)

    if diagnostics:
        return "\n\n".join(diagnostics)

    fallback = []
    for line in lines:
        clean = _strip_error_prefix(line).strip()
        if not clean or MAVEN_NOISE_RE.search(clean):
            continue
        if line.lstrip().startswith("[ERROR]"):
            fallback.append(clean)

    return "\n".join(fallback[:80]).strip()


def _get_target_repo_path(deps: Any) -> Optional[str]:
    """Support current RustPrint deps plus the planned Java-oriented deps."""

    for attr in (
        "absolute_java_output_path",
        "java_workspace_path",
        "absolute_rust_output_path",
        "rust_workspace_path",
        "absolute_rust_repo_path",
    ):
        value = getattr(deps, attr, None)
        if value:
            return str(value)
    return None


def _resolve_working_dir(workspace_root: Path, working_dir: Optional[str]) -> Path:
    if not working_dir:
        return workspace_root
    candidate = (workspace_root / working_dir.lstrip("/")).resolve()
    try:
        candidate.relative_to(workspace_root.resolve())
    except ValueError:
        raise ValueError("working_dir must stay inside the Java workspace.")
    if candidate.is_file():
        return candidate.parent
    return candidate


def _find_maven_project_dir(start: Path, workspace_root: Path) -> Optional[Path]:
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


async def maven_compile(
    ctx: RunContext[Any],
    working_dir: Optional[str] = None,
    timeout_seconds: int = 300,
) -> str:
    """Run `mvn -q -DskipTests compile` for the Java workspace or module.

    Args:
        working_dir: Optional path relative to the translated Java workspace.
            If it points inside a Maven module, compilation runs from the nearest
            parent directory containing `pom.xml`. If omitted, compilation runs
            from the workspace root.
        timeout_seconds: Subprocess timeout. Defaults to 300 seconds.
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
    except ValueError as exc:
        return f"Error: {exc}"

    if not requested_dir.exists():
        return f"Error: working_dir does not exist in Java workspace: {working_dir}"

    project_dir = _find_maven_project_dir(requested_dir, workspace_root)
    if project_dir is None:
        return f"Error: No pom.xml found at or above {requested_dir}."

    timeout_seconds = max(1, min(int(timeout_seconds), 900))
    cmd = ["mvn", "-q", "-DskipTests", "-Dstyle.color=never", "compile"]
    env = {**os.environ, "MAVEN_OPTS": os.environ.get("MAVEN_OPTS", "")}

    logger.info("=" * 80)
    logger.info("TOOL CALL: maven_compile")
    logger.info("  Workspace   : %s", workspace_root)
    logger.info("  Working dir : %s", working_dir or "(workspace root)")
    logger.info("  CWD         : %s", project_dir)
    logger.info("  Command     : cd %s && %s", project_dir, " ".join(cmd))
    logger.info("=" * 80)

    try:
        result = subprocess.run(
            cmd,
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            env=env,
        )
    except subprocess.TimeoutExpired:
        logger.warning("[maven_compile] timeout (%ss)", timeout_seconds)
        return (
            f"Error: Maven compile timed out after {timeout_seconds} seconds. "
            "Try narrowing the working_dir or simplifying the generated code."
        )
    except FileNotFoundError:
        logger.warning("[maven_compile] mvn not found")
        return "Error: 'mvn' command not found. Ensure Maven is installed and on PATH."
    except Exception as exc:
        logger.exception("[maven_compile] subprocess error: %s", exc)
        return f"Error running Maven compile: {exc}"

    stdout = result.stdout or ""
    stderr = result.stderr or ""
    raw_output = f"{stdout}\n{stderr}"
    logger.info("[maven_compile] exit_code=%s stdout:\n%s\nstderr:\n%s", result.returncode, stdout, stderr)

    if result.returncode != 0:
        attempts = getattr(deps, "maven_compile_attempts", 0) + 1
        setattr(deps, "maven_compile_attempts", attempts)
        filtered = filter_maven_compile_errors(raw_output, workspace_root=workspace_root)
        if not filtered:
            filtered = "(Maven failed, but no javac diagnostics were found. Check pom.xml or dependency configuration.)"
        return (
            f"Still has Maven compile errors. Iteration {attempts}.\n\n"
            "Fix the Java code or Maven configuration according to the errors below, then call maven_compile again.\n\n"
            "<MAVEN_COMPILE_ERRORS>\n"
            f"{filtered}\n"
            "</MAVEN_COMPILE_ERRORS>"
        )

    setattr(deps, "maven_compile_attempts", 0)
    logger.info("[maven_compile] Done. Maven compile passed (exit 0).")
    return "Done. Maven compile passed. Proceed to the next step."


maven_compile_tool = Tool(
    function=maven_compile,
    name="maven_compile",
    description=(
        "Run `mvn -q -DskipTests compile` in the translated Java Maven project. "
        "Optional working_dir is relative to the Java workspace; the tool runs from the nearest pom.xml. "
        "If compilation fails, it returns filtered actionable javac diagnostics only."
    ),
    takes_ctx=True,
)
