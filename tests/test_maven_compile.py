import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "rustprint/src/agent_tools/maven_compile.py"
SPEC = importlib.util.spec_from_file_location("maven_compile", MODULE_PATH)
maven_compile = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(maven_compile)

filter_maven_compile_errors = maven_compile.filter_maven_compile_errors


SUCCESSFUL_BUILD_LOG = """
[INFO] Scanning for projects...
[INFO]
[INFO] --------------------< com.example:demo >---------------------
[INFO] Building demo 1.0-SNAPSHOT
[INFO] --------------------------------[ jar ]---------------------------------
[INFO]
[INFO] --- maven-resources-plugin:3.3.1:resources (default-resources) @ demo ---
[INFO] skip non existing resourceDirectory /workspace/demo/src/main/resources
[INFO] --- maven-compiler-plugin:3.11.0:compile (default-compile) @ demo ---
[INFO] Nothing to compile - all classes are up to date
[INFO] ------------------------------------------------------------------------
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
[INFO] Total time:  1.234 s
[INFO] Finished at: 2026-06-24T10:00:00+07:00
"""


FAILED_BUILD_LOG_WITH_STACK_TRACE = """
[INFO] Scanning for projects...
[INFO] Reactor Build Order:
[INFO] demo-parent                                                        [pom]
[INFO] core                                                               [jar]
[INFO]
[ERROR] COMPILATION ERROR :
[ERROR] /workspace/demo/core/src/main/java/com/example/core/Foo.java:[12,34] cannot find symbol
[ERROR]   symbol:   variable missingValue
[ERROR]   location: class com.example.core.Foo
[ERROR] /workspace/demo/core/src/main/java/com/example/core/Bar.java:[27,16] incompatible types: java.lang.String cannot be converted to int
[ERROR] /workspace/demo/core/src/main/java/com/example/core/Baz.java:[44,9] unreported exception java.io.IOException; must be caught or declared to be thrown
[ERROR] Failed to execute goal org.apache.maven.plugins:maven-compiler-plugin:3.11.0:compile (default-compile) on project core: Compilation failure
[ERROR] /workspace/demo/core/src/main/java/com/example/core/Foo.java:[12,34] cannot find symbol
[ERROR] To see the full stack trace of the errors, re-run Maven with the -e switch.
[ERROR] Re-run Maven using the -X switch to enable full debug logging.
[ERROR]
[ERROR] For more information about the errors and possible solutions, please read the following articles:
[ERROR] [Help 1] http://cwiki.apache.org/confluence/display/MAVEN/MojoFailureException
org.apache.maven.lifecycle.LifecycleExecutionException: Failed to execute goal
    at org.apache.maven.lifecycle.internal.MojoExecutor.doExecute2(MojoExecutor.java:375)
    at org.apache.maven.lifecycle.internal.MojoExecutor.doExecute(MojoExecutor.java:351)
Caused by: org.apache.maven.plugin.compiler.CompilationFailureException: Compilation failure
    at org.apache.maven.plugin.compiler.AbstractCompilerMojo.execute(AbstractCompilerMojo.java:1212)
"""


ANSI_COLORED_FAILURE_LOG = """
\x1b[31m[ERROR]\x1b[0m /workspace/demo/src/main/java/com/example/App.java:[8,13] ';' expected
\x1b[31m[ERROR]\x1b[0m Failed to execute goal org.apache.maven.plugins:maven-compiler-plugin:compile
"""


def test_successful_build_log_has_no_actionable_errors():
    assert filter_maven_compile_errors(SUCCESSFUL_BUILD_LOG, Path("/workspace/demo")) == ""


def test_failed_build_log_extracts_only_clean_compiler_diagnostics():
    filtered = filter_maven_compile_errors(
        FAILED_BUILD_LOG_WITH_STACK_TRACE,
        Path("/workspace/demo"),
    )

    assert "core/src/main/java/com/example/core/Foo.java:[12,34] cannot find symbol" in filtered
    assert "symbol:   variable missingValue" in filtered
    assert "location: class com.example.core.Foo" in filtered
    assert "core/src/main/java/com/example/core/Bar.java:[27,16] incompatible types" in filtered
    assert "core/src/main/java/com/example/core/Baz.java:[44,9] unreported exception" in filtered

    assert "BUILD FAILURE" not in filtered
    assert "Failed to execute goal" not in filtered
    assert "full stack trace" not in filtered
    assert "LifecycleExecutionException" not in filtered
    assert "MojoExecutor" not in filtered
    assert "Help 1" not in filtered

    assert filtered.count("Foo.java:[12,34]") == 1


def test_ansi_codes_are_stripped():
    filtered = filter_maven_compile_errors(ANSI_COLORED_FAILURE_LOG, Path("/workspace/demo"))

    assert filtered == "src/main/java/com/example/App.java:[8,13] ';' expected"
    assert "\x1b" not in filtered
