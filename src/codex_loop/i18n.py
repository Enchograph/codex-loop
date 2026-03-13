from __future__ import annotations

from dataclasses import dataclass


DEFAULT_LANGUAGE = "en"
BUILTIN_LANGUAGES = {"en", "zh-CN"}


@dataclass(frozen=True)
class Messages:
    language_name: str
    interactive_title: str
    choose_command: str
    prompt_repo: str
    using_current_repo: str
    prompt_path_optional: str
    prompt_language: str
    prompt_yes_no: str
    invalid_option: str
    run_requires_docs: str


MESSAGES = {
    "en": Messages(
        language_name="English",
        interactive_title="Codex Loop interactive mode",
        choose_command="Choose a command",
        prompt_repo="Repository path",
        using_current_repo="Using current directory as repository",
        prompt_path_optional="Path (optional)",
        prompt_language="Document language",
        prompt_yes_no="Enter y or n, or press Enter for the default.",
        invalid_option="Enter the number of a listed option, or press Enter for the default.",
        run_requires_docs="The repository is missing generated relay docs or runtime config.",
    ),
    "zh-CN": Messages(
        language_name="中文",
        interactive_title="Codex Loop 交互模式",
        choose_command="请选择命令",
        prompt_repo="仓库路径",
        using_current_repo="当前目录将作为仓库",
        prompt_path_optional="路径（可选）",
        prompt_language="文档语言",
        prompt_yes_no="请输入 y 或 n，或直接回车使用默认值。",
        invalid_option="请输入列表中的数字，或直接回车使用默认值。",
        run_requires_docs="仓库缺少已生成的接力文档或运行配置。",
    ),
}


def resolve_language(language: str | None) -> str:
    if language in MESSAGES:
        return language
    if language:
        return language
    return DEFAULT_LANGUAGE


def get_messages(language: str | None) -> Messages:
    resolved = resolve_language(language)
    return MESSAGES.get(resolved, MESSAGES[DEFAULT_LANGUAGE])
