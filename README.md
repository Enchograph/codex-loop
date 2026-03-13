# Codex Loop

Codex Loop is a Python CLI project for running fully automated Codex relay development.

The project is divided into three parts:

1. Optionally generate a "base requirements document" for an existing repository, or let AI help refine the detailed project requirements document you wrote yourself.
   We recommend directly using your detailed project requirements document for step two. The quality of this document determines the final runtime quality.
2. Generate the document set from the "base requirements document", so Codex sessions can continue development seamlessly across multiple relay rounds.
3. Run unattended fully automated `codex exec` development loops based on that document set.

If you only need an automatic loop script suitable for Codex, see `codex-loop-minimal/`, or run `codex-loop run` directly and choose `Use loop script only`.

The project supports Windows, macOS, Linux, and similar systems, and requires Python 3.11 or above.

## Install

```bash
python -m pip install -e .
```

## Commands

Running `codex-loop` directly uses the current terminal directory as the repository by default, and lets the user choose command parameters one by one.

```bash
cd /path/to/repo
codex-loop
```

You can also explicitly specify the repository path with `--repo`.

### Step 1 (optional): generate / refine the "base requirements document"

Used to generate the "base requirements document" for an existing code repository. It can also refine a user-provided document into the "base requirements document".

We more strongly recommend writing a detailed "base requirements document" yourself and taking it directly into the second stage. The quality of this "base requirements document" determines the final runtime quality.

#### Generate the document from scratch for an existing code repository:

```bash
codex-loop draft
```

This command should not be run inside an empty repository.

#### Refine a user-provided document:

```bash
codex-loop draft --requirements-doc /path/to/original-user-doc.md
```

### Step 2: document set generation

Step 2: generate the development rules that Codex sessions should follow from the "base requirements document".

It requires the "base requirements document" to exist.
If you did not run step 1:
then you need to place your document at `.codex-loop/docs/USER-REQUIREMENTS.md`,
or explicitly specify the "base requirements document" path through `--requirements-doc`.

#### `USER-REQUIREMENTS.md` (the "base requirements document") already exists:

```bash
codex-loop prepare
```

#### Explicitly specify the "base requirements document" path:

```bash
codex-loop prepare --requirements-doc /path/to/user-requirements.md
```

### Step 3, automatic loop execution

Start multi-round automatic `codex exec` development loops from the generated `.codex-loop/config/codex-loop.json`.

```bash
codex-loop run
```
