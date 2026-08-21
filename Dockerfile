# Runtime image for the c2java (rustprint) migration pipeline.
#
# The pipeline shells out to `mvn` and needs a JDK to compile the generated
# Java project; Node is declared in pyproject.toml [external] for mermaid-py
# diagram validation. `npm` is separate from `nodejs` on Ubuntu and is required
# at *build* time: mermaid-parser-py -> pythonmonkey -> pminit ships sdist-only
# and its post-install hook aborts if npm is missing.
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LANG=C.UTF-8 \
    PATH="/opt/venv/bin:${PATH}"

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        python3.12 \
        python3.12-venv \
        openjdk-17-jdk-headless \
        maven \
        nodejs \
        npm \
        git \
        ca-certificates \
        build-essential \
        curl \
        less \
    && rm -rf /var/lib/apt/lists/*

# Own virtualenv so pip is not blocked by PEP 668 (externally-managed-environment).
RUN python3.12 -m venv /opt/venv \
    && pip install --no-cache-dir --upgrade pip setuptools wheel

WORKDIR /workspace/c2java

COPY . .

# `tiktoken` is imported by rustprint/src/utils.py but missing from the
# pyproject dependency list, so it is installed explicitly.
RUN pip install --no-cache-dir -e ".[dev]" tiktoken

# Editable install keeps ROOT_DIR (= /workspace/c2java) correct at runtime, so
# the bind-mounted host checkout is what actually executes.

CMD ["bash"]
