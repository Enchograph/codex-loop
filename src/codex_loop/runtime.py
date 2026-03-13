from __future__ import annotations

import json
import signal
import subprocess
import time
from pathlib import Path

from codex_loop.codex import build_exec_command
from codex_loop.models import RuntimeConfig, SUPPORTED_APPROVAL_POLICIES, SUPPORTED_RUN_MODES, SUPPORTED_SANDBOX_MODES


def load_config(path: Path) -> RuntimeConfig:
    payload = json.loads(path.read_text(encoding="utf-8"))
    config = RuntimeConfig(
        codex_bin=payload.get("codex_bin", "codex"),
        workdir=Path(payload["workdir"]).resolve(),
        prompt=payload["prompt"],
        total_timeout_minutes=int(payload.get("total_timeout_minutes", 300)),
        run_mode=payload.get("run_mode", "relay-docs"),
        log_dir=Path(payload["log_dir"]).resolve() if payload.get("log_dir") else None,
        skip_git_repo_check=bool(payload.get("skip_git_repo_check", False)),
        sandbox_mode=payload.get("sandbox_mode", "workspace-write"),
        approval_policy=payload.get("approval_policy", "on-request"),
        search_enabled=bool(payload.get("search_enabled", True)),
        profile=payload.get("profile"),
        model=payload.get("model"),
        extra_args=list(payload.get("extra_args", [])),
    )
    validate_runtime_config(config)
    return config


def validate_runtime_config(config: RuntimeConfig) -> None:
    if config.run_mode not in SUPPORTED_RUN_MODES:
        raise ValueError(f"Unsupported run mode: {config.run_mode}")
    if config.sandbox_mode not in SUPPORTED_SANDBOX_MODES:
        raise ValueError(f"Unsupported sandbox mode: {config.sandbox_mode}")
    if config.approval_policy not in SUPPORTED_APPROVAL_POLICIES:
        raise ValueError(f"Unsupported approval policy: {config.approval_policy}")
    if not config.workdir.exists():
        raise FileNotFoundError(f"Workdir not found: {config.workdir}")
    if config.total_timeout_minutes <= 0:
        raise ValueError("total_timeout_minutes must be greater than zero")


class LoopRunner:
    def __init__(self, config: RuntimeConfig) -> None:
        self.config = config
        self._child: subprocess.Popen[str] | None = None

    def run(self) -> int:
        deadline = time.time() + self.config.total_timeout_minutes * 60
        round_number = 1
        log_dir = (self.config.log_dir or (self.config.workdir / ".codex-loop" / "log")).resolve()
        log_dir.mkdir(parents=True, exist_ok=True)

        try:
            while True:
                remaining = int(deadline - time.time())
                if remaining <= 0:
                    print("Total timeout reached before starting a new round.")
                    return 0
                exit_code = self._run_round(round_number, log_dir)
                if exit_code != 0:
                    print(f"Round {round_number} exited with code {exit_code}.")
                round_number += 1
        except KeyboardInterrupt:
            self._stop_child()
            print("\nStop requested.")
            return 130

    def _run_round(self, round_number: int, log_dir: Path) -> int:
        run_id = time.strftime("%Y%m%d-%H%M%S")
        round_dir = log_dir / f"round-{round_number}-{run_id}"
        round_dir.mkdir(parents=True, exist_ok=True)
        stdout_path = round_dir / "stdout.log"
        stderr_path = round_dir / "stderr.log"
        final_path = round_dir / "final-message.txt"

        command = build_exec_command(self.config)
        command.extend(["--output-last-message", str(final_path), self.config.prompt])

        print(f"=== Round {round_number} ===")
        print(f"Logs: {round_dir}")

        with stdout_path.open("w", encoding="utf-8") as stdout_file, stderr_path.open("w", encoding="utf-8") as stderr_file:
            self._child = subprocess.Popen(
                command,
                cwd=self.config.workdir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL,
                text=True,
                bufsize=1,
                creationflags=_creationflags(),
            )
            assert self._child.stdout is not None
            assert self._child.stderr is not None
            try:
                for line in self._child.stdout:
                    print(line, end="")
                    stdout_file.write(line)
                for line in self._child.stderr:
                    print(line, end="")
                    stderr_file.write(line)
            finally:
                exit_code = self._child.wait()
                self._child = None

        if final_path.exists() and final_path.stat().st_size > 0:
            print("\n--- Final message ---")
            print(final_path.read_text(encoding="utf-8"))
        return exit_code

    def _stop_child(self) -> None:
        if not self._child:
            return
        try:
            if hasattr(signal, "CTRL_BREAK_EVENT"):
                self._child.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                self._child.send_signal(signal.SIGINT)
            self._child.wait(timeout=3)
        except Exception:
            self._child.terminate()
            try:
                self._child.wait(timeout=3)
            except Exception:
                self._child.kill()


def _creationflags() -> int:
    return getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
