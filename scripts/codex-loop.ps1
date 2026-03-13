param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Args
)

python -m codex_loop @Args
