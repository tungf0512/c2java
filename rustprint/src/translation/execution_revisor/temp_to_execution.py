"""Convert Maven Surefire XML reports to execution.jsonl and result.json.

execution.jsonl keeps the existing refinement contract: one JSON object per
executed test, with failing/error tests carrying concise stdout.
result.json keeps aggregate pass/fail counts and rates.
"""

from __future__ import annotations

import json
import logging
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

FRAME_RE = re.compile(
    r"^\s*at\s+(?P<class>[\w.$]+)\.(?P<method>[\w$<>]+)"
    r"\((?P<file>[^:()]+\.java):(?P<line>\d+)\)"
)
EXCEPTION_RE = re.compile(
    r"^(?P<exception>(?:[\w$]+\.)*(?:AssertionError|AssertionFailedError|NullPointerException|"
    r"IllegalArgumentException|IllegalStateException|IndexOutOfBoundsException|RuntimeException|Exception|Error))"
    r"(?::\s*(?P<message>.*))?$"
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


def _strip_namespace(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def _iter_testcases(root: ET.Element):
    for elem in root.iter():
        if _strip_namespace(elem.tag) == "testcase":
            yield elem


def _children_named(elem: ET.Element, name: str) -> list[ET.Element]:
    return [child for child in list(elem) if _strip_namespace(child.tag) == name]


def _child_text(elem: ET.Element, name: str) -> str:
    parts = []
    for child in _children_named(elem, name):
        if child.text:
            parts.append(child.text)
    return "\n".join(parts).strip()


def _is_internal_frame(class_name: str) -> bool:
    return class_name.startswith(INTERNAL_FRAME_PREFIXES)


def _short_exception_name(name: str) -> str:
    return name.rsplit(".", 1)[-1]


def _extract_failure_reason(raw_text: str, fallback_message: str = "") -> str:
    """Return concise failure reason and first application/test source frame."""

    raw_text = raw_text or ""
    lines = raw_text.replace("\r\n", "\n").replace("\r", "\n").splitlines()
    current_exception: Optional[str] = None
    current_message = ""
    first_nonempty = ""
    best_frame: Optional[tuple[str, str]] = None

    for idx, line in enumerate(lines):
        clean = line.strip()
        if clean and not first_nonempty:
            first_nonempty = clean

        exc = EXCEPTION_RE.match(clean)
        if exc:
            current_exception = _short_exception_name(exc.group("exception"))
            current_message = (exc.group("message") or "").strip()
            if not current_message and idx + 1 < len(lines):
                next_line = lines[idx + 1].strip()
                if next_line and not next_line.startswith("at "):
                    current_message = next_line
            continue

        frame = FRAME_RE.match(clean)
        if not frame:
            continue
        frame_class = frame.group("class")
        if _is_internal_frame(frame_class):
            continue
        best_frame = (f"{frame.group('file')}:{frame.group('line')}", f"{frame_class}.{frame.group('method')}")
        break

    reason = ""
    if current_exception:
        reason = f"{current_exception}: {current_message}".rstrip(": ")
    elif fallback_message:
        reason = fallback_message.strip()
    elif first_nonempty:
        reason = first_nonempty

    if best_frame:
        location, test_ref = best_frame
        if reason:
            return f"Test: {test_ref}\nLocation: {location}\nReason: {reason}"
        return f"Test: {test_ref}\nLocation: {location}"
    return reason


def _class_to_test_path(classname: str, report_path: Path, repo_root: Path) -> str:
    rel_report = report_path.resolve().relative_to(repo_root.resolve())
    parts = rel_report.parts
    module_parts: tuple[str, ...] = ()
    if "target" in parts:
        target_idx = parts.index("target")
        module_parts = parts[:target_idx]

    java_rel = Path(*classname.split(".")).with_suffix(".java") if classname else Path("UnknownTest.java")
    candidate = repo_root.joinpath(*module_parts, "src", "test", "java", java_rel)
    if candidate.exists():
        return str(candidate.relative_to(repo_root)).replace("\\", "/")

    if module_parts:
        return str(Path(*module_parts, "src", "test", "java", java_rel)).replace("\\", "/")
    return str(Path("src", "test", "java", java_rel)).replace("\\", "/")


def _test_name(classname: str, method: str) -> str:
    short_class = classname.rsplit(".", 1)[-1] if classname else "UnknownTest"
    return f"{short_class}#{method or 'unknown'}"


def parse_surefire_report(report_path: Path, repo_root: Path) -> list[dict]:
    """Parse one TEST-*.xml file into execution records."""

    report_path = Path(report_path)
    repo_root = Path(repo_root)
    root = ET.parse(report_path).getroot()
    records: list[dict] = []

    for case in _iter_testcases(root):
        classname = case.attrib.get("classname", "")
        method = case.attrib.get("name", "")
        elapsed = case.attrib.get("time")
        failure_nodes = _children_named(case, "failure")
        error_nodes = _children_named(case, "error")
        skipped_nodes = _children_named(case, "skipped")

        if skipped_nodes:
            status = "skip"
        elif failure_nodes or error_nodes:
            status = "fail"
        else:
            status = "pass"

        rec = {
            "name": _test_name(classname, method),
            "status": status,
            "path": _class_to_test_path(classname, report_path, repo_root),
        }
        if elapsed not in (None, ""):
            try:
                rec["exec_time"] = float(elapsed)
            except ValueError:
                rec["exec_time"] = elapsed

        if status == "fail":
            failure_texts = []
            for node in failure_nodes + error_nodes:
                message = node.attrib.get("message", "")
                text = (node.text or "").strip()
                failure_texts.append(_extract_failure_reason(text, fallback_message=message))
            stdout_parts = [part for part in failure_texts if part]
            system_out = _child_text(case, "system-out") or _child_text(root, "system-out")
            system_err = _child_text(case, "system-err") or _child_text(root, "system-err")
            if system_out:
                stdout_parts.append(system_out)
            if system_err:
                stdout_parts.append(system_err)
            rec["stdout"] = "\n\n".join(stdout_parts).strip()

        records.append(rec)

    return records


def _find_reports(repo_root: Path) -> list[Path]:
    return sorted(Path(repo_root).resolve().glob("**/target/surefire-reports/TEST-*.xml"))


def convert_surefire_reports_to_execution_and_result(repo_root: Path) -> tuple[Path, Path]:
    """Scan repo_root for Surefire XML and write execution.jsonl/result.json."""

    repo_root = Path(repo_root).resolve()
    if not repo_root.is_dir():
        raise NotADirectoryError(f"repo_root is not a directory: {repo_root}")

    execution_path = repo_root / "execution.jsonl"
    result_path = repo_root / "result.json"
    reports = _find_reports(repo_root)

    records: list[dict] = []
    for report in reports:
        try:
            records.extend(parse_surefire_report(report, repo_root))
        except ET.ParseError as exc:
            logger.warning("Could not parse Surefire report %s: %s", report, exc)

    pass_count = sum(1 for rec in records if rec.get("status") == "pass")
    failed_count = sum(1 for rec in records if rec.get("status") == "fail")
    num_tests = len(records)
    pass_rate = (pass_count / num_tests) if num_tests else 0.0
    failed_rate = (failed_count / num_tests) if num_tests else 0.0

    with open(execution_path, "w") as handle:
        for rec in records:
            handle.write(json.dumps(rec) + "\n")

    result_obj = {
        "num_tests": num_tests,
        "pass_count": pass_count,
        "pass_rate": round(pass_rate, 4),
        "failed_count": failed_count,
        "failed_rate": round(failed_rate, 4),
    }
    with open(result_path, "w") as handle:
        json.dump(result_obj, handle, indent=2)

    logger.info(
        "Wrote %s (%d lines) and %s (reports=%d, num_tests=%d, pass=%d, fail=%d)",
        execution_path.name,
        len(records),
        result_path.name,
        len(reports),
        num_tests,
        pass_count,
        failed_count,
    )
    return execution_path, result_path


def convert_temp_to_execution_and_result(path: Path) -> tuple[Path, Path]:
    """Backward-compatible entry point.

    Old callers passed `temp.jsonl`; Java/Maven callers should pass the repo
    root. If a file path is provided, use its parent as the repo root.
    """

    path = Path(path).resolve()
    repo_root = path if path.is_dir() else path.parent
    return convert_surefire_reports_to_execution_and_result(repo_root)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Convert Maven Surefire XML reports to execution.jsonl and result.json")
    parser.add_argument("repo_root", type=Path, help="Path to the Maven repository root")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)
    convert_surefire_reports_to_execution_and_result(args.repo_root)


if __name__ == "__main__":
    main()
