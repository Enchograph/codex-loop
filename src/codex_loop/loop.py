from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TextIO


@dataclass
class LoopConfig:
    codex_bin: str | None
    codex_command: list[str] | None
    workdir: Path
    prompt: str
    total_timeout_minutes: int
    max_rounds: int | None
    log_dir: Path | None
    skip_git_repo_check: bool
    sandbox_mode: str
    approval_policy: str
    search_enabled: bool
    profile: str | None
    model: str | None
    extra_args: list[str]

    @property
    def total_timeout_seconds(self) -> int:
        return self.total_timeout_minutes * 60

    @property
    def resolved_log_dir(self) -> Path:
        if self.log_dir is not None:
            return self.log_dir
        return self.workdir / ".codex" / "log"


def load_config(path: Path) -> LoopConfig:
    data = json.loads(path.read_text(encoding="utf-8"))
    codex_command = data.get("codex_command")
    if codex_command is not None and not isinstance(codex_command, list):
        raise ValueError("codex_command must be a list of strings or null")
    if codex_command is not None and not all(isinstance(item, str) for item in codex_command):
        raise ValueError("codex_command must contain only strings")
    timeout_minutes = data.get("total_timeout_minutes")
    if timeout_minutes is None:
        timeout_seconds = int(data.get("total_timeout_seconds", 0))
        timeout_minutes = max(1, timeout_seconds // 60)
    return LoopConfig(
        codex_bin=data.get("codex_bin"),
        codex_command=codex_command,
        workdir=Path(data["workdir"]).resolve(),
        prompt=data["prompt"],
        total_timeout_minutes=int(timeout_minutes),
        max_rounds=int(data["max_rounds"]) if data.get("max_rounds") is not None else None,
        log_dir=Path(data["log_dir"]).resolve() if data.get("log_dir") else None,
        skip_git_repo_check=bool(data["skip_git_repo_check"]),
        sandbox_mode=data["sandbox_mode"],
        approval_policy=data["approval_policy"],
        search_enabled=bool(data["search_enabled"]),
        profile=data.get("profile"),
        model=data.get("model"),
        extra_args=list(data.get("extra_args", [])),
    )


class LoopRunner:
    def __init__(self, config: LoopConfig) -> None:
        self.config = config
        self.stop_requested = False
        self.current_process: subprocess.Popen[str] | None = None

    def run(self) -> int:
        self._validate()
        self._install_signal_handlers()
        log_dir = self.config.resolved_log_dir
        log_dir.mkdir(parents=True, exist_ok=True)

        deadline = time.time() + self.config.total_timeout_seconds
        round_number = 1

        print(f"Config file loaded for workdir: {self.config.workdir}")
        print(f"Log dir: {log_dir}")

        while True:
            if self.stop_requested:
                print("Stopped.")
                return 130
            if self.config.max_rounds is not None and round_number > self.config.max_rounds:
                print("Reached configured round limit. Exiting.")
                return 0

            remaining = int(deadline - time.time())
            if remaining <= 0:
                print("Total timeout reached before starting a new round. Exiting.")
                return 0

            run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
            round_dir = log_dir / f"round-{round_number}-{run_id}"
            round_dir.mkdir(parents=True, exist_ok=True)
            stdout_log = round_dir / "stdout.log"
            stderr_log = round_dir / "stderr.log"
            final_log = round_dir / "final-message.txt"

            print(f"=== Round {round_number} ===")
            print(f"Remaining total budget: {(remaining + 59) // 60} minute(s)")
            print(f"Logs: {round_dir}")

            exit_code = self._run_round(self._build_command(final_log), stdout_log, stderr_log)

            if final_log.exists() and final_log.read_text(encoding="utf-8").strip():
                print("\n--- Final message ---")
                print(final_log.read_text(encoding="utf-8"))

            if exit_code == 130:
                print(f"Round {round_number} interrupted.")
            elif exit_code == 0:
                print(f"Round {round_number} finished successfully.")
            else:
                print(f"Round {round_number} exited with code {exit_code}.")

            if self.stop_requested:
                print("Stopped.")
                return 130
            if time.time() >= deadline:
                print("Total timeout reached. Current round finished, exiting.")
                return 0
            round_number += 1

    def _validate(self) -> None:
        if not self.config.workdir.exists():
            raise FileNotFoundError(f"Workdir not found: {self.config.workdir}")
        command = self.config.codex_command or [self.config.codex_bin or "codex"]
        executable = command[0]
        if Path(executable).exists():
            return
        if shutil.which(executable) is None:
            raise FileNotFoundError(f"Codex executable not found: {executable}")

    def _build_command(self, final_log: Path) -> list[str]:
        command = list(self.config.codex_command or [self.config.codex_bin or "codex"])
        command.append("exec")
        if self.config.skip_git_repo_check:
            command.append("--skip-git-repo-check")
        if self.config.approval_policy == "never":
            if self.config.sandbox_mode == "danger-full-access":
                command.append("--dangerously-bypass-approvals-and-sandbox")
            else:
                command.extend(["--sandbox", self.config.sandbox_mode])
        elif self.config.approval_policy in {"on-failure", "on-request", "untrusted"}:
            command.extend(["--ask-for-approval", self.config.approval_policy])
            command.extend(["--sandbox", self.config.sandbox_mode])
        else:
            raise ValueError(f"Unsupported approval_policy: {self.config.approval_policy}")

        command.extend(["--cd", str(self.config.workdir)])
        if self.config.search_enabled:
            command.append("--search")
        if self.config.profile:
            command.extend(["--profile", self.config.profile])
        if self.config.model:
            command.extend(["--model", self.config.model])
        if self.config.extra_args:
            command.extend(self.config.extra_args)
        command.extend(["-o", str(final_log), self.config.prompt])
        return command

    def _run_round(self, command: list[str], stdout_log: Path, stderr_log: Path) -> int:
        with stdout_log.open("w", encoding="utf-8") as stdout_file, stderr_log.open(
            "w", encoding="utf-8"
        ) as stderr_file:
            process = subprocess.Popen(
                command,
                cwd=self.config.workdir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            self.current_process = process
            stdout_thread = threading.Thread(
                target=_stream_pipe, args=(process.stdout, sys.stdout, stdout_file), daemon=True
            )
            stderr_thread = threading.Thread(
                target=_stream_pipe, args=(process.stderr, sys.stderr, stderr_file), daemon=True
            )
            stdout_thread.start()
            stderr_thread.start()
            process.wait()
            stdout_thread.join()
            stderr_thread.join()
            if process.stdout is not None:
                process.stdout.close()
            if process.stderr is not None:
                process.stderr.close()
            self.current_process = None
            return int(process.returncode or 0)

    def _install_signal_handlers(self) -> None:
        def handler(_signum: int, _frame: object) -> None:
            self.stop_requested = True
            print("\nStop requested. Terminating current round...")
            if self.current_process is None:
                return
            if os.name == "nt":
                try:
                    self.current_process.send_signal(signal.CTRL_BREAK_EVENT)
                except Exception:
                    self.current_process.terminate()
            else:
                self.current_process.send_signal(signal.SIGINT)
                time.sleep(1)
                if self.current_process.poll() is None:
                    self.current_process.terminate()

        signal.signal(signal.SIGINT, handler)
        if hasattr(signal, "SIGTERM"):
            signal.signal(signal.SIGTERM, handler)


def _stream_pipe(pipe: TextIO | None, console: TextIO, file_obj: TextIO) -> None:
    if pipe is None:
        return
    for line in pipe:
        console.write(line)
        console.flush()
        file_obj.write(line)
        file_obj.flush()
