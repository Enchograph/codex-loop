param(
    [string]$ConfigFile = "codex_supervised_loop.json"
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ConfigPath = Join-Path $ScriptDir $ConfigFile

if (-not (Test-Path $ConfigPath)) {
    throw "Config file not found: $ConfigPath"
}

$Config = Get-Content -Raw $ConfigPath | ConvertFrom-Json

$CodexBin = [string]$Config.codex_bin
$Workdir = [string]$Config.workdir
$Prompt = [string]$Config.prompt
$TotalTimeoutMinutes = if ($null -ne $Config.total_timeout_minutes) { [int]$Config.total_timeout_minutes } else { [int]([int]$Config.total_timeout_seconds / 60) }
$LogDir = if ($null -ne $Config.log_dir -and [string]$Config.log_dir -ne "") { [string]$Config.log_dir } else { Join-Path $Workdir ".codex\log" }
$SkipGitRepoCheck = [bool]$Config.skip_git_repo_check
$SandboxMode = [string]$Config.sandbox_mode
$ApprovalPolicy = [string]$Config.approval_policy
$SearchEnabled = [bool]$Config.search_enabled
$Profile = if ($null -ne $Config.profile) { [string]$Config.profile } else { $null }
$Model = if ($null -ne $Config.model) { [string]$Config.model } else { $null }
$ExtraArgs = @()
if ($null -ne $Config.extra_args) {
    foreach ($Arg in $Config.extra_args) {
        $ExtraArgs += [string]$Arg
    }
}

if (-not (Get-Command $CodexBin -ErrorAction SilentlyContinue)) {
    throw "Codex binary not found: $CodexBin"
}

if (-not (Test-Path $Workdir)) {
    throw "Workdir not found: $Workdir"
}

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

$CodexArgs = @("exec")
if ($SkipGitRepoCheck) {
    $CodexArgs += "--skip-git-repo-check"
}

switch ($ApprovalPolicy) {
    "never" {
        if ($SandboxMode -eq "danger-full-access") {
            $CodexArgs += "--dangerously-bypass-approvals-and-sandbox"
        }
        else {
            $CodexArgs += @("--sandbox", $SandboxMode)
        }
    }
    "on-failure" { $CodexArgs += @("--ask-for-approval", $ApprovalPolicy, "--sandbox", $SandboxMode) }
    "on-request" { $CodexArgs += @("--ask-for-approval", $ApprovalPolicy, "--sandbox", $SandboxMode) }
    "untrusted" { $CodexArgs += @("--ask-for-approval", $ApprovalPolicy, "--sandbox", $SandboxMode) }
    default { throw "Unsupported approval_policy: $ApprovalPolicy" }
}

$CodexArgs += @("--cd", $Workdir)
if ($SearchEnabled) {
    $CodexArgs += "--search"
}
if ($Profile) {
    $CodexArgs += @("--profile", $Profile)
}
if ($Model) {
    $CodexArgs += @("--model", $Model)
}
if ($ExtraArgs.Count -gt 0) {
    $CodexArgs += $ExtraArgs
}

$Deadline = (Get-Date).AddMinutes($TotalTimeoutMinutes)
$Round = 1

Write-Host "Config file: $ConfigPath"
Write-Host "Codex binary: $CodexBin"
Write-Host "Workdir: $Workdir"
Write-Host "Total timeout: $TotalTimeoutMinutes minute(s)"
Write-Host "Log dir: $LogDir"
Write-Host ""

while ($true) {
    if ((Get-Date) -ge $Deadline) {
        Write-Host "Total timeout reached before starting a new round. Exiting."
        exit 0
    }

    $RunId = Get-Date -Format "yyyyMMdd-HHmmss"
    $RoundLogDir = Join-Path $LogDir "round-$Round-$RunId"
    New-Item -ItemType Directory -Force -Path $RoundLogDir | Out-Null
    $StdoutLog = Join-Path $RoundLogDir "stdout.log"
    $StderrLog = Join-Path $RoundLogDir "stderr.log"
    $FinalMsgLog = Join-Path $RoundLogDir "final-message.txt"

    Write-Host "=== Round $Round ==="
    $RemainingMinutes = [int][Math]::Ceiling(($Deadline - (Get-Date)).TotalMinutes)
    Write-Host "Remaining total budget: $RemainingMinutes minute(s)"
    Write-Host "Logs: $RoundLogDir"

    $RoundArgs = @()
    $RoundArgs += $CodexArgs
    $RoundArgs += @("-o", $FinalMsgLog, $Prompt)

    & $CodexBin @RoundArgs 2>&1 | Tee-Object -FilePath $StdoutLog | Tee-Object -FilePath $StderrLog
    $ExitCode = $LASTEXITCODE

    switch ($ExitCode) {
        130 { Write-Host "Round $Round interrupted." }
        0 { Write-Host "Round $Round finished successfully." }
        default { Write-Host "Round $Round exited with code $ExitCode." }
    }

    if (Test-Path $FinalMsgLog) {
        $FinalText = Get-Content -Raw $FinalMsgLog
        if ($FinalText.Trim()) {
            Write-Host ""
            Write-Host "--- Final message ---"
            Write-Host $FinalText
        }
    }

    if ((Get-Date) -ge $Deadline) {
        Write-Host "Total timeout reached. Current round finished, exiting."
        exit 0
    }

    $Round += 1
    Write-Host ""
}
