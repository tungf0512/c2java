import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "rustprint/src/translation/execution_revisor/temp_to_execution.py"
SPEC = importlib.util.spec_from_file_location("temp_to_execution", MODULE_PATH)
temp_to_execution = importlib.util.module_from_spec(SPEC)
sys.modules["temp_to_execution"] = temp_to_execution
assert SPEC.loader is not None
SPEC.loader.exec_module(temp_to_execution)


PASSING_XML = """<?xml version="1.0" encoding="UTF-8"?>
<testsuite name="com.example.CalculatorTest" tests="2" failures="0" errors="0" skipped="0">
  <testcase classname="com.example.CalculatorTest" name="addsNumbers" time="0.001"/>
  <testcase classname="com.example.CalculatorTest" name="subtractsNumbers" time="0.002"/>
</testsuite>
"""


FAILING_XML = """<?xml version="1.0" encoding="UTF-8"?>
<testsuite name="com.example.UserServiceTest" tests="2" failures="1" errors="1" skipped="0">
  <testcase classname="com.example.UserServiceTest" name="loadsUser" time="0.004">
    <error message="Cannot invoke &quot;com.example.User.getName()&quot; because &quot;user&quot; is null" type="java.lang.NullPointerException">java.lang.NullPointerException: Cannot invoke "com.example.User.getName()" because "user" is null
    at com.example.UserServiceTest.loadsUser(UserServiceTest.java:31)
    at org.junit.platform.commons.util.ReflectionUtils.invokeMethod(ReflectionUtils.java:728)
    at org.apache.maven.surefire.junitplatform.JUnitPlatformProvider.execute(JUnitPlatformProvider.java:184)
    </error>
    <system-out>seed=123</system-out>
  </testcase>
  <testcase classname="com.example.UserServiceTest" name="rejectsMissingUser" time="0.006">
    <failure message="expected: &lt;true&gt; but was: &lt;false&gt;" type="org.opentest4j.AssertionFailedError">org.opentest4j.AssertionFailedError: expected: &lt;true&gt; but was: &lt;false&gt;
    at com.example.UserServiceTest.rejectsMissingUser(UserServiceTest.java:47)
    at org.junit.jupiter.engine.execution.MethodInvocation.proceed(MethodInvocation.java:60)
    </failure>
  </testcase>
</testsuite>
"""


def test_parse_passing_surefire_report(tmp_path):
    repo = tmp_path / "repo"
    report_dir = repo / "target/surefire-reports"
    test_src = repo / "src/test/java/com/example/CalculatorTest.java"
    report_dir.mkdir(parents=True)
    test_src.parent.mkdir(parents=True)
    test_src.write_text("package com.example; class CalculatorTest {}", encoding="utf-8")
    report = report_dir / "TEST-com.example.CalculatorTest.xml"
    report.write_text(PASSING_XML, encoding="utf-8")

    records = temp_to_execution.parse_surefire_report(report, repo)

    assert records == [
        {
            "name": "CalculatorTest#addsNumbers",
            "status": "pass",
            "path": "src/test/java/com/example/CalculatorTest.java",
            "exec_time": 0.001,
        },
        {
            "name": "CalculatorTest#subtractsNumbers",
            "status": "pass",
            "path": "src/test/java/com/example/CalculatorTest.java",
            "exec_time": 0.002,
        },
    ]


def test_parse_failing_multimodule_surefire_report(tmp_path):
    repo = tmp_path / "repo"
    report_dir = repo / "core/target/surefire-reports"
    test_src = repo / "core/src/test/java/com/example/UserServiceTest.java"
    report_dir.mkdir(parents=True)
    test_src.parent.mkdir(parents=True)
    test_src.write_text("package com.example; class UserServiceTest {}", encoding="utf-8")
    report = report_dir / "TEST-com.example.UserServiceTest.xml"
    report.write_text(FAILING_XML, encoding="utf-8")

    records = temp_to_execution.parse_surefire_report(report, repo)

    assert len(records) == 2
    assert records[0]["name"] == "UserServiceTest#loadsUser"
    assert records[0]["status"] == "fail"
    assert records[0]["path"] == "core/src/test/java/com/example/UserServiceTest.java"
    assert "Location: UserServiceTest.java:31" in records[0]["stdout"]
    assert "NullPointerException: Cannot invoke" in records[0]["stdout"]
    assert "seed=123" in records[0]["stdout"]
    assert "org.junit.platform" not in records[0]["stdout"]
    assert "org.apache.maven" not in records[0]["stdout"]

    assert records[1]["name"] == "UserServiceTest#rejectsMissingUser"
    assert records[1]["status"] == "fail"
    assert "Location: UserServiceTest.java:47" in records[1]["stdout"]
    assert "AssertionFailedError: expected: <true> but was: <false>" in records[1]["stdout"]
    assert "org.junit.jupiter" not in records[1]["stdout"]


def test_convert_surefire_reports_writes_execution_and_result(tmp_path):
    repo = tmp_path / "repo"
    pass_dir = repo / "target/surefire-reports"
    fail_dir = repo / "core/target/surefire-reports"
    pass_dir.mkdir(parents=True)
    fail_dir.mkdir(parents=True)
    (pass_dir / "TEST-com.example.CalculatorTest.xml").write_text(PASSING_XML, encoding="utf-8")
    (fail_dir / "TEST-com.example.UserServiceTest.xml").write_text(FAILING_XML, encoding="utf-8")

    execution_path, result_path = temp_to_execution.convert_surefire_reports_to_execution_and_result(repo)

    execution_records = [json.loads(line) for line in execution_path.read_text().splitlines()]
    result = json.loads(result_path.read_text())

    assert len(execution_records) == 4
    assert result == {
        "num_tests": 4,
        "pass_count": 2,
        "pass_rate": 0.5,
        "failed_count": 2,
        "failed_rate": 0.5,
    }
