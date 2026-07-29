"""Static scanner for risky Java patterns in translated Java repos."""

from __future__ import annotations

import logging
import re
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

RISK_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("unsafe_api", re.compile(r"\b(?:sun\.misc|jdk\.internal\.misc)\.Unsafe\b")),
    ("jni_native", re.compile(r"\bnative\b")),
    ("system_exit", re.compile(r"\bSystem\s*\.\s*exit\s*\(")),
    ("runtime_exec", re.compile(r"\bRuntime\s*\.\s*getRuntime\s*\(\s*\)\s*\.\s*exec\s*\(")),
    ("process_builder", re.compile(r"\bnew\s+ProcessBuilder\s*\(")),
    ("reflection_set_accessible", re.compile(r"\.\s*setAccessible\s*\(\s*true\s*\)")),
)


def count_java_risk_patterns(source: str) -> int:
    """Count risky Java pattern occurrences in a source string."""

    total = 0
    for _, pattern in RISK_PATTERNS:
        total += len(pattern.findall(source or ""))
    return total


def java_risk_details(source: str) -> dict[str, int]:
    """Return per-risk counts for diagnostics and tests."""

    return {name: len(pattern.findall(source or "")) for name, pattern in RISK_PATTERNS}


def _get_target_repo_path(deps: Any) -> Optional[str]:
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


async def java_risk_detect(
    ctx: RunContext[Any],
    module: str = "",
) -> str:
    """Scan translated Java files for risky or non-portable patterns."""

    deps = ctx.deps
    repo_path = _get_target_repo_path(deps)
    if not repo_path:
        msg = "Error: No Java repository path in deps."
        logger.warning("[java_risk_detect] %s", msg)
        return msg

    repo_root = Path(repo_path).resolve()
    if not repo_root.is_dir():
        msg = f"Error: Java repo path is not a directory: {repo_root}"
        logger.warning("[java_risk_detect] %s", msg)
        return msg

    logger.info("=" * 80)
    logger.info("TOOL CALL: java_risk_detect")
    logger.info("  Module : %s", module or "(unspecified)")
    logger.info("  Path   : %s", repo_root)
    logger.info("=" * 80)

    lines: list[str] = []
    for path in sorted(repo_root.rglob("*.java")):
        if "target" in path.relative_to(repo_root).parts:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        count = count_java_risk_patterns(text)
        if count > 0:
            rel = path.relative_to(repo_root)
            lines.append(f"FILE {rel} has {count} risk block(s)")

    if not lines:
        out = "No risky blocks detected."
        logger.info("[java_risk_detect] module=%s %s", module, out)
        return out

    out = "\n".join(lines)
    logger.info("[java_risk_detect] module=%s results:\n%s", module, out)
    return out


java_risk_detect_tool = Tool(
    function=java_risk_detect,
    name="java_risk_detect",
    description=(
        "Scan translated Java files for risky or non-portable patterns: sun.misc.Unsafe, "
        "jdk.internal.misc.Unsafe, native methods, System.exit, Runtime.exec, ProcessBuilder, "
        "and setAccessible(true). Returns lines like 'FILE path has n risk block(s)'."
    ),
    takes_ctx=True,
)
