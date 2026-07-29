"""Tool to run one JUnit test via Maven Surefire with concise failure output."""

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

try:
    from .maven_compile import _get_target_repo_path, _resolve_working_dir, _strip_ansi
    from .maven_test_compile import _build_maven_command
except ImportError:  # pragma: no cover - direct file import in unit tests.
    from maven_compile import _get_target_repo_path, _resolve_working_dir, _strip_ansi  # type: ignore[no-redef]
    from maven_test_compile import _build_maven_command  # type: ignore[no-redef]

logger = logging.getLogger(__name__)

ERROR_PREFIX_RE = re.compile(r"^\s*(?:\[ERROR\]\s*)?")
SUMMARY_FAILURE_RE = re.compile(
    r"^(?P<test>[\w.$]+):(?P<line>\d+)\s*(?:[»:]?\s*)?(?P<message>.+)$"
)
EXCEPTION_RE = re.compile(
    r"^(?P<exception>(?:[\w$]+\.)*(?:AssertionError|AssertionFailedError|NullPointerException|"
    r"IllegalArgumentException|IllegalStateException|IndexOutOfBoundsException|RuntimeException|Exception|Error))"
    r"(?::\s*(?P<message>.*))?$"
)
FRAME_RE = re.compile(
    r"^\s*at\s+(?P<class>[\w.$]+)\.(?P<method>[\w$<>]+)"
    r"\((?P<file>[^:()]+\.java):(?P<line>\d+)\)"
)
INTERNAL_FRAME_PREFIXES = (
    "org.junit.",
    "org.junit.jupiter.",
    "org.junit.platform.",
    "org.opentest4j.",
    "org.apache.maven.",
    "org.codehaus.",
    "java.",
    "javax.",
    "jdk.",
    "sun.",
)


def _clean_line(line: str) -> str:
    return ERROR_PREFIX_RE.sub("", _strip_ansi(line)).strip()


def _is_internal_frame(class_name: str) -> bool:
    return class_name.startswith(INTERNAL_FRAME_PREFIXES)


def _short_exception_name(name: str) -> str:
    return name.rsplit(".", 1)[-1]


def _method_from_selector(selector: Optional[str]) -> Optional[str]:
    if not selector:
        return None
    if "#" in selector:
        return selector.rsplit("#", 1)[-1]
    if "." in selector:
        return selector.rsplit(".", 1)[-1]
    return selector


def _render_failure(
    reason: str,
    location: Optional[str] = None,
    test_name: Optional[str] = None,
) -> str:
    lines = []
    if test_name:
        lines.append(f"Test: {test_name}")
    if location:
        lines.append(f"Location: {location}")
    lines.append(f"Reason: {reason}")
    return "\n".join(lines)


def filter_maven_single_test_failure(raw_output: str, test_name: Optional[str] = None) -> str:
    """Extract one actionable JUnit/Surefire failure from noisy Maven output."""

    lines = _strip_ansi(raw_output).replace("\r\n", "\n").replace("\r", "\n").splitlines()
    wanted_method = _method_from_selector(test_name)

    current_exception: Optional[str] = None
    current_message: str = ""
    best_fallback: Optional[tuple[str, str, str]] = None

    for idx, line in enumerate(lines):
        clean = _clean_line(line)
        if not clean:
            continue

        exc = EXCEPTION_RE.match(clean)
        if exc:
            current_exception = _short_exception_name(exc.group("exception"))
            current_message = (exc.group("message") or "").strip()
            if not current_message and idx + 1 < len(lines):
                next_line = _clean_line(lines[idx + 1])
                if next_line and not next_line.startswith("at "):
                    current_message = next_line
            continue

        frame = FRAME_RE.match(clean)
        if not frame or not current_exception:
            continue

        frame_class = frame.group("class")
        frame_method = frame.group("method")
        if _is_internal_frame(frame_class):
            continue
        if wanted_method and frame_method != wanted_method:
            if best_fallback is None:
                best_fallback = (
                    f"{current_exception}: {current_message}".rstrip(": "),
                    f"{frame.group('file')}:{frame.group('line')}",
                    f"{frame_class}.{frame_method}",
                )
            continue

        reason = f"{current_exception}: {current_message}".rstrip(": ")
        location = f"{frame.group('file')}:{frame.group('line')}"
        return _render_failure(reason, location=location, test_name=f"{frame_class}.{frame_method}")

    if best_fallback is not None:
        reason, location, fallback_test = best_fallback
        return _render_failure(reason, location=location, test_name=fallback_test)

    summary_candidates: list[tuple[str, str, str]] = []
    for line in lines:
        clean = _clean_line(line)
        match = SUMMARY_FAILURE_RE.match(clean)
        if not match:
            continue
        summary_test = match.group("test")
        if "." not in summary_test:
            continue
        if wanted_method and not summary_test.endswith(f".{wanted_method}"):
            continue
        location = f"{summary_test.rsplit('.', 1)[0]}.java:{match.group('line')}"
        message = match.group("message").strip()
        summary_candidates.append((summary_test, location, message))

    if summary_candidates:
        summary_test, location, message = summary_candidates[0]
        return _render_failure(message, location=location, test_name=summary_test)

    fallback_lines = []
    for line in lines:
        clean = _clean_line(line)
        if not clean:
            continue
        if clean.startswith(("Failed to execute goal", "To see the full stack trace", "Re-run Maven", "For more information", "[Help")):
            continue
        if "org.junit.platform" in clean or "org.apache.maven" in clean or "sun.reflect" in clean:
            continue
        if "ERROR" in line or "Exception" in clean or "Assertion" in clean:
            fallback_lines.append(clean)
    return "\n".join(fallback_lines[:20]).strip()


def _normalize_test_selector(raw_name: str, deps: Any) -> str:
    name = (raw_name or "").strip()
    if not name:
        return name
    if "#" in name:
        return name
    class_name = getattr(deps, "current_test_class_name", None) or getattr(deps, "current_test_class", None)
    if class_name:
        return f"{class_name}#{name}"
    if "." in name:
        class_part, method = name.rsplit(".", 1)
        return f"{class_part}#{method}"
    return f"*#{name}"


async def maven_single_test(
    ctx: RunContext[Any],
    test_name: Optional[str] = None,
    working_dir: Optional[str] = None,
    timeout_seconds: int = 180,
) -> str:
    """Run the current failing JUnit test through Maven Surefire."""

    deps = ctx.deps
    repo_path = _get_target_repo_path(deps)
    if not repo_path:
        return "Error: No Java repository path in deps."

    raw_test_name = test_name or getattr(deps, "current_test_name", None) or ""
    selector = _normalize_test_selector(raw_test_name, deps)
    if not selector:
        return "Error: No current_test_name in deps and no test_name argument provided."

    workspace_root = Path(repo_path).resolve()
    if not workspace_root.is_dir():
        return f"Error: Java repo path is not a directory: {workspace_root}"

    effective_working_dir = working_dir or getattr(deps, "current_test_path", None) or getattr(deps, "current_path", None)
    try:
        requested_dir = _resolve_working_dir(workspace_root, effective_working_dir)
        cwd, cmd, module_path = _build_maven_command(
            workspace_root,
            requested_dir,
            [f"-Dtest={selector}", "-Dstyle.color=never", "test"],
        )
    except (ValueError, FileNotFoundError) as exc:
        return f"Error: {exc}"

    timeout_seconds = max(1, min(int(timeout_seconds), 900))
    env = {**os.environ, "MAVEN_OPTS": os.environ.get("MAVEN_OPTS", "")}

    logger.info("=" * 80)
    logger.info("TOOL CALL: maven_single_test")
    logger.info("  Test        : %s", selector)
    logger.info("  Workspace   : %s", workspace_root)
    logger.info("  Working dir : %s", effective_working_dir or "(workspace root)")
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
        logger.warning("[maven_single_test] timeout (%ss)", timeout_seconds)
        return f"Error: Maven single-test run timed out after {timeout_seconds} seconds."
    except FileNotFoundError:
        logger.warning("[maven_single_test] mvn not found")
        return "Error: 'mvn' command not found. Ensure Maven is installed and on PATH."
    except Exception as exc:
        logger.exception("[maven_single_test] subprocess error: %s", exc)
        return f"Error running Maven single test: {exc}"

    stdout = result.stdout or ""
    stderr = result.stderr or ""
    raw_output = f"{stdout}\n{stderr}"
    logger.info("[maven_single_test] exit_code=%s stdout:\n%s\nstderr:\n%s", result.returncode, stdout, stderr)

    if result.returncode != 0:
        filtered = filter_maven_single_test_failure(raw_output, test_name=selector)
        if not filtered:
            filtered = "(Maven test failed, but no concise Surefire failure could be extracted.)"
        return f"Test failed.\n<SUREFIRE_FAILURE>\n{filtered}\n</SUREFIRE_FAILURE>"

    logger.info("[maven_single_test] test passed.")
    return "Test passed."


maven_single_test_tool = Tool(
    function=maven_single_test,
    name="maven_single_test",
    description=(
        "Run one JUnit test using Maven Surefire. Uses current_test_name from context unless test_name is provided. "
        "Runs `mvn -q -Dtest=ClassName#methodName test`, with `-pl <module> -am` when scoped inside a Maven module. "
        "On failure, returns only the assertion/exception reason and test source location."
    ),
    takes_ctx=True,
)
