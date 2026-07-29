import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _load_tool_module(module_name: str, relative_path: str):
    path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


maven_compile = _load_tool_module("maven_compile", "rustprint/src/agent_tools/maven_compile.py")
maven_test_compile = _load_tool_module(
    "maven_test_compile",
    "rustprint/src/agent_tools/maven_test_compile.py",
)
maven_single_test = _load_tool_module(
    "maven_single_test",
    "rustprint/src/agent_tools/maven_single_test.py",
)

filter_maven_test_compile_errors = maven_test_compile.filter_maven_test_compile_errors
filter_maven_single_test_failure = maven_single_test.filter_maven_single_test_failure


TEST_COMPILE_FAILURE_LOG = """
[INFO] Scanning for projects...
[ERROR] COMPILATION ERROR :
[ERROR] /workspace/demo/src/test/java/com/example/FooTest.java:[19,28] cannot find symbol
[ERROR]   symbol:   method missingHelper()
[ERROR]   location: class com.example.FooTest
[ERROR] Failed to execute goal org.apache.maven.plugins:maven-compiler-plugin:3.11.0:testCompile (default-testCompile) on project demo: Compilation failure
[ERROR] To see the full stack trace of the errors, re-run Maven with the -e switch.
org.apache.maven.lifecycle.LifecycleExecutionException: noisy stack trace
"""


SUREFIRE_ASSERTION_FAILURE_LOG = """
[INFO] -------------------------------------------------------
[INFO]  T E S T S
[INFO] -------------------------------------------------------
[ERROR] Failures:
[ERROR]   CalculatorTest.addsNumbers:42 expected: <5> but was: <4>
[ERROR] Tests run: 3, Failures: 1, Errors: 0, Skipped: 0
[ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:3.2.5:test (default-test) on project demo: There are test failures.
[ERROR] To see the full stack trace of the errors, re-run Maven with the -e switch.
[ERROR] Re-run Maven using the -X switch to enable full debug logging.
"""


SUREFIRE_NPE_STACK_TRACE_LOG = """
[ERROR] com.example.UserServiceTest.loadsUser -- Time elapsed: 0.004 s <<< ERROR!
java.lang.NullPointerException: Cannot invoke "com.example.User.getName()" because "user" is null
    at com.example.UserServiceTest.loadsUser(UserServiceTest.java:31)
    at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke0(Native Method)
    at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:77)
    at org.junit.platform.commons.util.ReflectionUtils.invokeMethod(ReflectionUtils.java:728)
    at org.junit.jupiter.engine.execution.MethodInvocation.proceed(MethodInvocation.java:60)
    at org.apache.maven.surefire.junitplatform.JUnitPlatformProvider.execute(JUnitPlatformProvider.java:184)
[ERROR] Errors:
[ERROR]   UserServiceTest.loadsUser:31 NullPointer Cannot invoke "com.example.User.getName()" because "user" is null
[ERROR] Tests run: 1, Failures: 0, Errors: 1, Skipped: 0
[ERROR] Failed to execute goal org.apache.maven.plugins:maven-surefire-plugin:3.2.5:test (default-test) on project demo: There are test failures.
"""


def test_maven_test_compile_reuses_clean_compiler_filtering():
    filtered = filter_maven_test_compile_errors(TEST_COMPILE_FAILURE_LOG, Path("/workspace/demo"))

    assert filtered == (
        "src/test/java/com/example/FooTest.java:[19,28] cannot find symbol\n"
        "  symbol:   method missingHelper()\n"
        "  location: class com.example.FooTest"
    )
    assert "LifecycleExecutionException" not in filtered
    assert "Failed to execute goal" not in filtered


def test_surefire_assertion_summary_is_reduced_to_reason_and_location():
    filtered = filter_maven_single_test_failure(
        SUREFIRE_ASSERTION_FAILURE_LOG,
        test_name="CalculatorTest#addsNumbers",
    )

    assert filtered == (
        "Test: CalculatorTest.addsNumbers\n"
        "Location: CalculatorTest.java:42\n"
        "Reason: expected: <5> but was: <4>"
    )
    assert "maven-surefire-plugin" not in filtered
    assert "full stack trace" not in filtered


def test_surefire_exception_stack_trace_keeps_app_frame_only():
    filtered = filter_maven_single_test_failure(
        SUREFIRE_NPE_STACK_TRACE_LOG,
        test_name="UserServiceTest#loadsUser",
    )

    assert filtered == (
        "Test: com.example.UserServiceTest.loadsUser\n"
        "Location: UserServiceTest.java:31\n"
        "Reason: NullPointerException: Cannot invoke \"com.example.User.getName()\" because \"user\" is null"
    )
    assert "org.junit.platform" not in filtered
    assert "org.apache.maven" not in filtered
    assert "jdk.internal.reflect" not in filtered
