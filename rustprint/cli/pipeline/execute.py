import logging
import os
import subprocess
from pathlib import Path

from rustprint.src.translation.execution_revisor.temp_to_execution import convert_surefire_reports_to_execution_and_result

logger = logging.getLogger(__name__)


def _has_maven_modules(repo_path: Path) -> bool:
    pom = repo_path / "pom.xml"
    if not pom.is_file():
        return False
    try:
        text = pom.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    return "<modules>" in text and "</modules>" in text


def _run_maven_tests(repo_path: Path) -> None:
    env = os.environ.copy()
    temp_path = repo_path / "temp.log"
    cmd = ["mvn", "-q", "-Dstyle.color=never"]
    if _has_maven_modules(repo_path):
        cmd.append("-fae")
    cmd.append("test")
    with open(temp_path, "w") as handle:
        subprocess.run(
            cmd,
            cwd=str(repo_path),
            env=env,
            stdout=handle,
            stderr=subprocess.STDOUT,
            check=False,
        )


def _process_repo(repo_path: Path) -> None:
    name = repo_path.name
    if not (repo_path / "pom.xml").is_file():
        logger.info("Skip %s (no pom.xml)", name)
        return
    if (repo_path / "result.json").is_file():
        logger.info("Skip %s (result.json exists)", name)
        return

    logger.info("--- %s ---", name)
    if not (repo_path / "temp.log").is_file():
        _run_maven_tests(repo_path)
    try:
        convert_surefire_reports_to_execution_and_result(repo_path)
    except Exception as exc:
        logger.warning("Conversion failed for %s: %s", name, exc)


def run(version, output_root) -> None:
    output_root = Path(output_root)
    version_dir = output_root / "translated_repos" / "execution-aware" / f"version_{version}"
    if not version_dir.is_dir():
        raise RuntimeError(f"Not a directory: {version_dir}")

    for repo_path in sorted(version_dir.iterdir()):
        if repo_path.is_dir():
            _process_repo(repo_path)


def run_single(repo_path) -> None:
    repo_path = Path(repo_path).resolve()
    if not repo_path.is_dir():
        raise RuntimeError(f"--single_repo path is not a directory: {repo_path}")
    _process_repo(repo_path)
