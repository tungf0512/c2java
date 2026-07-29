import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "rustprint/src/agent_tools/java_risk_detect.py"
SPEC = importlib.util.spec_from_file_location("java_risk_detect", MODULE_PATH)
java_risk_detect = importlib.util.module_from_spec(SPEC)
sys.modules["java_risk_detect"] = java_risk_detect
assert SPEC.loader is not None
SPEC.loader.exec_module(java_risk_detect)

count_java_risk_patterns = java_risk_detect.count_java_risk_patterns
java_risk_details = java_risk_detect.java_risk_details


SAFE_JAVA = """
package com.example;

public final class SafeMath {
    public int add(int a, int b) {
        return a + b;
    }
}
"""


RISKY_JAVA = """
package com.example;

import sun.misc.Unsafe;

public final class RiskyApp {
    private native void callNative();

    public void stopNow() {
        System.exit(1);
    }

    public void runShell() throws Exception {
        Runtime.getRuntime().exec("rm -rf /tmp/example");
        new ProcessBuilder("sh", "-c", "echo hi").start();
    }

    public void breakEncapsulation() throws Exception {
        var field = RiskyApp.class.getDeclaredField("secret");
        field.setAccessible(true);
    }
}
"""


def test_safe_java_has_no_risk_patterns():
    assert count_java_risk_patterns(SAFE_JAVA) == 0
    assert all(count == 0 for count in java_risk_details(SAFE_JAVA).values())


def test_risky_java_counts_each_target_pattern():
    details = java_risk_details(RISKY_JAVA)

    assert details == {
        "unsafe_api": 1,
        "jni_native": 1,
        "system_exit": 1,
        "runtime_exec": 1,
        "process_builder": 1,
        "reflection_set_accessible": 1,
    }
    assert count_java_risk_patterns(RISKY_JAVA) == 6


def test_java_risk_detect_reports_files_and_ignores_target_dir(tmp_path):
    repo = tmp_path / "repo"
    risky_file = repo / "src/main/java/core/App.java"
    safe_file = repo / "src/main/java/core/SafeMath.java"
    generated_file = repo / "target/generated/Generated.java"

    risky_file.parent.mkdir(parents=True)
    generated_file.parent.mkdir(parents=True)
    risky_file.write_text(RISKY_JAVA, encoding="utf-8")
    safe_file.write_text(SAFE_JAVA, encoding="utf-8")
    generated_file.write_text("public class Generated { public native void x(); }", encoding="utf-8")

    ctx = SimpleNamespace(deps=SimpleNamespace(java_workspace_path=str(repo)))

    import asyncio

    result = asyncio.run(java_risk_detect.java_risk_detect(ctx, module="core"))

    assert result == "FILE src/main/java/core/App.java has 6 risk block(s)"
    assert "target/generated/Generated.java" not in result
