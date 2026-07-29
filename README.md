# C2Java

C2Java is an AI-assisted tool that translates C repositories into Java/Maven projects. It analyzes the C source and headers, builds documentation and dependency information, generates Java code, optionally translates tests, and validates the result with Maven.

The command-line package is still named `rustprint` for compatibility with the original project. Despite that name, this repository uses the C-to-Java translator in `rustprint/src/translation/code/c2java_*` and produces Java output.

## Requirements

- Python 3.12 or newer
- Java 17 or newer
- Maven 3.8 or newer
- Node.js 14 or newer (used by `mermaid-py` to validate diagrams)
- An OpenAI-compatible LLM endpoint and API key

The source repository must contain at least one `.c` or `.h` file. A `pom.xml` is generated in the Java output; Maven is used during execution-aware validation.

## Install

Clone with the bundled C fixture submodules:

```bash
git clone --recurse-submodules https://github.com/tungf0512/c2java.git
cd c2java
```

Create a virtual environment and install the package:

```bash
python3 -m venv .venv
source .venv/bin/activate       # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
```

Verify the CLI is available:

```bash
rustprint --help
rustprint version
```

## Configure a C project

Run `init` with the path to the C repository. The command is interactive and stores a project-specific TOML file at `~/.config/rustprint/<project-name>`:

```bash
rustprint init /absolute/path/to/my-c-project
cd /absolute/path/to/my-c-project
```

The setup asks for the model, API endpoint, output directories, and refinement options. The default output locations are:

- Final Java repository: `~/rustprint-output/<project-name>`
- Intermediate cache and run artifacts: `~/.cache/rustprint/<project-name>`

To inspect or change settings later:

```bash
rustprint config show
rustprint config set model.name gpt-5.4
rustprint config set api.base_url https://api.openai.com/v1
rustprint config set requirement_refinement.rounds 3
rustprint config set execution_refinement.rounds 3
```

The relevant configuration has this shape:

```toml
[model]
name = "gpt-5.4"
provider = "openai"

[source]
path = "/absolute/path/to/my-c-project"

[api]
api_key = ""
base_url = "https://api.openai.com/v1"

[output]
base_dir = "~/rustprint-output"
cache = "~/.cache/rustprint"

[requirement_refinement]
enabled = true
rounds = 5

[execution_refinement]
enabled = true
rounds = 5
translate_tests = true
```

For safer local use, leave `api_key` empty and provide credentials through environment variables instead:

```bash
export LLM_API_KEY="your-api-key"
export LLM_BASE_URL="https://api.openai.com/v1"
```

Environment variables take precedence over values in the project config. Never commit API keys; local configuration files such as `llm_config.json` and `.env` are ignored by Git.

## Translate C to Java

Run the migration from the configured C repository directory:

```bash
cd /absolute/path/to/my-c-project
rustprint migrate
```

By default, the command starts a live tracker at `http://127.0.0.1:5000`. Useful options are:

```bash
rustprint migrate --no-web       # terminal-only execution
rustprint migrate --port 5050   # use another tracker port
rustprint migrate --force       # discard this project's cache and restart
```

The pipeline performs these stages:

1. Parse C source and generate module/dependency documentation.
2. Generate an initial Java project with `src/main/java` and `pom.xml`.
3. Refine generated code against documented requirements (when enabled).
4. Translate C tests into Java tests (when enabled).
5. Compile and run Maven tests, then refine failures (when execution refinement is enabled).
6. Copy the best validated result to the configured final output directory.

When complete, the CLI prints the final Java repository path. Build or test it independently with:

```bash
cd ~/rustprint-output/my-c-project
mvn test
```

Review generated Java carefully before production use. C pointer ownership, macros, platform-specific behavior, undefined behavior, and native-library integration may require manual changes even when Maven tests pass.

## Outputs and troubleshooting

Intermediate artifacts are kept in the configured cache, including C documentation, translated versions, refinement logs, and test results. This makes it possible to inspect failures or rerun without starting over.

- Use `rustprint migrate --force` after changing the source or configuration when cached results are no longer valid.
- If the configured source path is wrong, run `rustprint init --force /path/to/project` again.
- If migration reports missing credentials, set `LLM_API_KEY` and `LLM_BASE_URL` or update the `[api]` section.
- If Maven fails, inspect the generated project with `mvn test` and fix the reported Java/compiler or dependency issue.
- Use `rustprint web --host 0.0.0.0 --port 5000` to launch the tracker UI separately.

## Repository layout

```text
rustprint/                         Python CLI and migration pipeline
rustprint/src/translation/code/    C-to-Java generator and orchestrator
libcbor_output/                   Example generated Java/Maven output
dummy_c_project/                  Small C fixture for development/tests
tests/                            Python tests for Java migration tools
libcbor, libyaml, stb              Upstream source submodules
```

## Development checks

Install development dependencies and run the Python tests:

```bash
python -m pip install -e ".[dev]"
pytest
```

The repository also includes Maven test tooling tests and a checked-in example under `libcbor_output`; run `mvn test` there to validate that generated Java project.

## License

This project is released under the MIT License. See [LICENSE](LICENSE).
