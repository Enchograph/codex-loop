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

### Base Project Requirements Document Generation (Optional)

Prepare the base project document for an existing-code repository:

```bash
codex-loop plan-docs --repo /path/to/repo --requirements-doc /path/to/original-user-doc.md --input-doc /path/to/your-project-doc.md
codex-loop plan-docs --repo /path/to/repo --ai-doc-language zh-CN
```

### Generate the AI Development Documentation Set from the User's Base Project Requirements Document

#### Empty project, with a user-provided base document

```bash
codex-loop init blank --repo /path/to/repo --requirements-doc /path/to/requirements.md
```

#### Existing project, without a user-provided base document

```bash
```

After generating the user base project requirements document through the previous step, generate the AI development documentation set based on that document.

```bash
codex-loop init existing-code --repo /path/to/repo --ai-doc-language zh-CN
```

#### Existing project, with a user-provided base document

```bash
```

### Start the Codex Automation Script

Start the Codex auto loop after the documentation set is ready:

```bash
codex-loop run --config /path/to/repo/codex-loop.json
codex-loop run --config /path/to/repo/codex-loop.json --sandbox-mode danger-full-access --approval-policy never
```

## Project Docs

- [Other Specified Documents](codex-loop-docs/en/OTHER-SPECIFIED-DOCUMENTS.md)
- [Usage Guide](codex-loop-docs/en/USAGE.md)
- [Repository Structure](codex-loop-docs/en/REPOSITORY-STRUCTURE.md)
- [Methodology](codex-loop-docs/en/METHODOLOGY.md)
- [Contributing](codex-loop-docs/en/CONTRIBUTING.md)
