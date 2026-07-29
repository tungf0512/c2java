from pydantic_ai import Agent, UsageLimits
import logging
import os
import time
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

from rustprint.src.agent_tools.deps import TestTransDeps
from rustprint.src.agent_tools.str_replace_editor import str_replace_editor_tool
from rustprint.src.agent_tools.maven_test_compile import maven_test_compile_tool
from rustprint.src.agent_tools.maven_single_test import maven_single_test_tool
from rustprint.src.agent_tools.find_code_component import find_code_component_tool
from rustprint.src.llm_services import create_main_model
from rustprint.src.agent_retry import run_agent_with_retry
from rustprint.src.prompt_template import TEST_TRANS_PROMPT
from rustprint.src.config import Config

MAX_REQUESTS_TEST_TRANS = 500

_C_TEST_EXTENSIONS = {".c", ".h", ".cpp", ".cc", ".cxx"}
_C_TEST_DIR_NAMES = ["tests", "test", "Tests", "Test"]


def _list_c_test_entries(c_repo_root: Path) -> list:
    entries = []
    for dir_name in _C_TEST_DIR_NAMES:
        test_dir = c_repo_root / dir_name
        if test_dir.is_dir():
            for item in sorted(test_dir.iterdir()):
                if item.is_file() and item.suffix in _C_TEST_EXTENSIONS:
                    entries.append(f"{dir_name}/{item.name}")
                elif item.is_dir():
                    entries.append(f"{dir_name}/{item.name}/")
            break
    return entries


def log_info(msg: str, func_name: str = ""):
    if func_name:
        logger.info(f"[{func_name} @ test_trans_orchestrator.py] {msg}")
    else:
        logger.info(msg)


class TestTransOrchestrator:

    def __init__(self, config: Config):
        self.config = config
        self.model = create_main_model(config)

    def create_test_trans_agent(self) -> Agent:
        return Agent(
            self.model,
            name="TestTrans",
            deps_type=TestTransDeps,
            tools=[str_replace_editor_tool, maven_test_compile_tool, maven_single_test_tool, find_code_component_tool],
            system_prompt=TEST_TRANS_PROMPT,
            retries=2,
            end_strategy='early',
        )

    async def translate_tests_for_repo(
        self,
        repo_name: str,
        c_repo_path: str,
        rust_repo_path: str,
    ) -> Dict[str, Any]:
        start = time.time()
        log_info(f"Test translation: {repo_name}", "translate_tests_for_repo")
        log_info(f"  C repo: {c_repo_path}", "translate_tests_for_repo")
        log_info(f"  Java repo: {rust_repo_path}", "translate_tests_for_repo")

        project_section = """\
The translated repository is a Java/Maven project. Inspect root `pom.xml`, any child module `pom.xml` files, and `src/main/java/...` to determine package names and public APIs.

Place every translated JUnit 5 test under `src/test/java/<matching/package>/...` in the appropriate Maven module. Never put tests in `src/main/java`, never embed tests in production classes, and never write test files at the repository root."""

        c_test_entries = _list_c_test_entries(Path(c_repo_path))
        if c_test_entries:
            c_test_hint = "Known C test files/directories (relative to c_repo root):\n" + "\n".join(
                f"  {e}" for e in c_test_entries
            )
        else:
            c_test_hint = "Could not pre-scan C test files — discover them manually using working_dir='c_repo'."

        from pathlib import Path as _Path

        deps = TestTransDeps(
            absolute_c_repo_path=c_repo_path,
            absolute_rust_output_path=rust_repo_path,
            registry={},
            config=self.config,
        )

        agent = self.create_test_trans_agent()
        prompt = f"""Generate JUnit 5 tests from the C repository to the translated Java repository for '{repo_name}'. YOU MUST ENSURE there are at least 50 tests for the repo when the C suite contains enough independent scenarios.


=== JAVA/MAVEN PROJECT STRUCTURE ===
{project_section}

=== C TEST FILES (pre-scanned) ===
{c_test_hint}

=== WORKFLOW ===
Translate tests from the C repository to the Java repository for '{repo_name}'.

1. Use str_replace_editor(working_dir='c_repo', command='view', path='tests') or path='test' to discover C test files. If neither exists, try path='.' and look for test-related directories. List all test files and plan to translate every one.
2. Read every C test file carefully and in full with str_replace_editor(working_dir='c_repo', command='view', path='<relative path>') to understand its test structure, assertions, inputs, and expected outputs before translating.
3. Use str_replace_editor(working_dir='rust_repo', command='view', path='.') to explore the Java/Maven layout. Treat working_dir='rust_repo' as the legacy alias for the translated Java repository.
4. BEFORE writing each JUnit class, read the exact production Java file(s) under `src/main/java/...` that define the API under test. Use `view` or `find_code_component` to confirm package names, class names, record names, method signatures, and whether values are exposed through record accessors like `x()` instead of fields like `x`.
5. Translate tests into JUnit 5 classes under the matching `src/test/java/<package>/...` directory. Do not translate too many at a single time — only 5-7 tests, verify they compile, then continue.
6. If JUnit 5 is missing, update `pom.xml` with JUnit Jupiter only under `<scope>test</scope>`.
7. For each test, use the inputs and expected outputs from the C test as the reference. Adapt calls to the Java API's exact class names, package names, argument types, return types, and record accessors.
8. Never invent inner classes or test-only stand-ins for production types. Import and use the real generated Java classes.
9. After every single test file create or edit: call maven_test_compile(working_dir='<path_you_edited>') and fix all errors until "Done. Maven test-compile passed." Use maven_single_test(test_name='ClassName#methodName', working_dir='<path_you_edited>') for representative translated tests.
10. When done with all test files, call maven_test_compile(working_dir='.') for the full project. If errors remain, fix and call again until it passes.
"""

        try:
            result = await run_agent_with_retry(
                agent,
                prompt,
                deps=deps,
                message_history=None,
                usage_limits=UsageLimits(request_limit=MAX_REQUESTS_TEST_TRANS),
            )
            elapsed = time.time() - start
            log_info(f"Completed in {elapsed:.2f}s", "translate_tests_for_repo")
            return {
                "repo_name": repo_name,
                "success": True,
                "elapsed": elapsed,
                "result": result,
            }
        except Exception as e:
            elapsed = time.time() - start
            log_info(f"Failed after {elapsed:.2f}s: {e}", "translate_tests_for_repo")
            return {
                "repo_name": repo_name,
                "success": False,
                "elapsed": elapsed,
                "error": str(e),
            }
