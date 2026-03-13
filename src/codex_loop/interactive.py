from __future__ import annotations

from codex_loop.i18n import get_messages


def choose_option(prompt: str, options: list[str], default_index: int = 0, language: str | None = None) -> str:
    messages = get_messages(language)
    print(f"{prompt}:")
    for index, option in enumerate(options, start=1):
        suffix = " (default)" if index - 1 == default_index else ""
        print(f"  {index}. {option}{suffix}")
    while True:
        raw = input("> ").strip()
        if not raw:
            return options[default_index]
        if raw.isdigit():
            selected = int(raw) - 1
            if 0 <= selected < len(options):
                return options[selected]
        print(messages.invalid_option)


def prompt_text(prompt: str, default: str = "") -> str:
    label = f"{prompt} [{default}]" if default else f"{prompt} [leave empty to skip]"
    raw = input(f"{label}: ").strip()
    return raw or default


def prompt_bool(prompt: str, default: bool, language: str | None = None) -> bool:
    messages = get_messages(language)
    suffix = "Y/n" if default else "y/N"
    while True:
        raw = input(f"{prompt} [{suffix}]: ").strip().lower()
        if not raw:
            return default
        if raw in {"y", "yes"}:
            return True
        if raw in {"n", "no"}:
            return False
        print(messages.prompt_yes_no)
