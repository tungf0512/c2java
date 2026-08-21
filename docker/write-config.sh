#!/usr/bin/env bash
# Write ~/.config/rustprint/<project> non-interactively.
#
# `rustprint init` is an interactive prompt-only command; this writes the same
# TOML directly so a containerised run is reproducible. Values come from the
# environment (see .env.example).
set -euo pipefail

PROJECT_NAME="${C_PROJECT_NAME:?C_PROJECT_NAME is not set}"
SOURCE_PATH="/work/source/${PROJECT_NAME}"
CONFIG_DIR="${HOME}/.config/rustprint"
CONFIG_FILE="${CONFIG_DIR}/${PROJECT_NAME}"

if [ ! -d "${SOURCE_PATH}" ]; then
  echo "error: ${SOURCE_PATH} is not mounted; check C_SOURCE_DIR in .env" >&2
  exit 1
fi

mkdir -p "${CONFIG_DIR}"

# api_key is intentionally left empty: LLM_API_KEY / LLM_BASE_URL from the
# environment take precedence and keep the secret out of the config file.
cat > "${CONFIG_FILE}" <<EOF
[model]
name = "${MODEL:-gpt-5.4}"
provider = "openai"

[source]
path = "${SOURCE_PATH}"

[api]
api_key = ""
base_url = "${LLM_BASE_URL:-https://api.openai.com/v1}"

[output]
base_dir = "~/rustprint-output"
cache = "~/.cache/rustprint"

[git]
branch_enabled = false
branch_name = "rustprint-migration"
commit = false

[requirement_refinement]
enabled = ${REQUIREMENT_REFINEMENT:-false}
rounds = ${REQUIREMENT_ROUNDS:-2}

[execution_refinement]
enabled = ${EXECUTION_REFINEMENT:-false}
rounds = ${EXECUTION_ROUNDS:-2}
translate_tests = ${TRANSLATE_TESTS:-false}

[run]
force = false
EOF

echo "Wrote ${CONFIG_FILE}"
cat "${CONFIG_FILE}"
