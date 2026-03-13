# Codex Loop

<p align="center">English | <a href="./README.zh-CN.md">中文</a></p>

## Project Introduction

Codex Loop is a simple script project that aims to provide fully automated loop development for Codex.

The project is divided into three parts:

1. Generate a base project requirements document from the user's request, if needed.
2. Generate a complete documentation set from the base project requirements document generated in the previous step or provided by the user, so that multiple fresh Codex sessions can continue relay development seamlessly.
3. Start an automation script that opens a new Codex session after Codex finishes one task, so the next part of the work starts automatically and unattended. It provides parameter settings such as language, Codex permissions, and loop time.

The project supports both brand-new empty-project development and mid-stream development for repositories that already contain code.

The project supports systems such as Windows, macOS, and Linux, and requires Python 3.11 or above.

## Commands

### Install

```bash
python -m pip install -e .[dev]
```

Running `codex-loop` with no additional arguments now opens an interactive terminal UI so the user can choose the command and its parameter options step by step.

### Base Project Requirements Document Generation (Optional)

Prepare the base project document for an existing-code repository:

```bash
PROJECT_DIR="/path/to/repo"
ORIGINAL_USER_DOC="/path/to/original-user-doc.md"

codex-loop plan-docs --repo "$PROJECT_DIR" --requirements-doc "$ORIGINAL_USER_DOC"
```

### Generate the AI Development Documentation Set from the User's Base Project Requirements Document

#### Empty project, with a user-provided base document

```bash
PROJECT_DIR="/path/to/repo"
BASE_REQUIREMENTS_DOC="/path/to/requirements.md"

codex-loop init blank --repo "$PROJECT_DIR" --requirements-doc "$BASE_REQUIREMENTS_DOC"
```

#### Existing project, without a user-provided base document

```bash
PROJECT_DIR="/path/to/repo"
ORIGINAL_USER_DOC="/path/to/original-user-doc.md"

codex-loop plan-docs --repo "$PROJECT_DIR" --requirements-doc "$ORIGINAL_USER_DOC"
```

After generating the user base project requirements document through the previous step, generate the AI development documentation set based on that document.

```bash
PROJECT_DIR="/path/to/repo"

codex-loop init existing-code --repo "$PROJECT_DIR" --ai-doc-language zh-CN
```

#### Existing project, with an original requirements document

```bash
PROJECT_DIR="/path/to/repo"
ORIGINAL_USER_DOC="/path/to/original-user-doc.md"

codex-loop plan-docs --repo "$PROJECT_DIR" --requirements-doc "$ORIGINAL_USER_DOC"
codex-loop init existing-code --repo "$PROJECT_DIR" --ai-doc-language zh-CN
```

### Start the Codex Automation Script

Start the Codex auto loop after the documentation set is ready, and **pay attention to the permission settings you grant to Codex**.

> The recommended approach is to give Codex non-interrupting permissions inside an empty virtual machine if you want fully unattended automatic development.

```bash
PROJECT_DIR="/path/to/repo"
CONFIG_PATH="$PROJECT_DIR/codex-loop.json"

codex-loop run --config "$CONFIG_PATH"
codex-loop run --config "$CONFIG_PATH" --sandbox-mode danger-full-access --approval-policy never
```

If you only want the fixed-prompt automatic Codex conversation loop, see the `/codex-loop-minimal` folder.

## Project Docs

- [Other Specified Documents](codex-loop-docs/en/OTHER-SPECIFIED-DOCUMENTS.md)
- [Usage Guide](codex-loop-docs/en/USAGE.md)
- [Repository Structure](codex-loop-docs/en/REPOSITORY-STRUCTURE.md)
- [Methodology](codex-loop-docs/en/METHODOLOGY.md)
- [Contributing](codex-loop-docs/en/CONTRIBUTING.md)
