#!/usr/bin/env bash
# Verify the container has everything the pipeline shells out to.
set -u

echo "python : $(python --version 2>&1)"
echo "java   : $(java -version 2>&1 | head -1)"
echo "maven  : $(mvn -version 2>&1 | head -1)"
echo "node   : $(node --version 2>&1)"
echo "npm    : $(npm --version 2>&1)"
echo "cli    : $(rustprint version 2>&1 | head -1)"
echo
python - <<'PY'
import importlib
mods = ["tiktoken", "tree_sitter_c", "mermaid_parser", "mermaid", "pydantic_ai", "openai", "networkx", "click"]
for m in mods:
    try:
        importlib.import_module(m)
        print(f"  {m:16} OK")
    except Exception as e:
        print(f"  {m:16} FAIL  {type(e).__name__}: {e}")
PY
echo
echo "cwd    : $(pwd)"
echo "source : $(ls -1 /work/source/${C_PROJECT_NAME}/**/*.c /work/source/${C_PROJECT_NAME}/**/*.h 2>/dev/null | wc -l) C files visible"
