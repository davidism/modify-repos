from __future__ import annotations

from pathlib import Path
from shutil import which
from subprocess import CompletedProcess

from ..utils import run_cmd
from .base import Repo


class GitRepo(Repo):
    _git_exe = which("git")
    add_untracked: bool = False

    def git_cmd(self, *args: str | Path) -> CompletedProcess[str]:
        if self._git_exe is None:
            raise RuntimeError("Git is not installed.")

        return run_cmd(self._git_exe, *args)

    def reset_target(self) -> None:
        self.git_cmd("switch", "-f", self.script.target)
        self.git_cmd("reset", "--hard", self.script.full_target)
        self.git_cmd("pull", "--prune")

    def reset_branch(self) -> None:
        self.git_cmd("switch", "-C", self.script.branch, self.script.target)

    def needs_commit(self) -> bool:
        args = ["status", "--porcelain"]

        if not self.add_untracked:
            args.append("--untracked-files=no")

        return bool(self.git_cmd(*args).stdout)

    def commit(self) -> None:
        if self.add_untracked:
            self.add_files(all=True)
        else:
            self.add_files(update=True)

        self.git_cmd("commit", "--message", self.script.commit_message)

    def needs_submit(self) -> bool:
        return bool(self.git_cmd("cherry", self.script.full_target).stdout)

    def submit(self) -> None:
        self.git_cmd("switch", self.script.target)
        self.git_cmd("merge", "--ff-only", self.script.branch)
        self.git_cmd("push", "--dry-run")

    def add_files(
        self, *items: str | Path, update: bool = False, all: bool = False
    ) -> None:
        if all:
            self.git_cmd("add", "--all")

        if update:
            self.git_cmd("add", "--update")

        self.git_cmd("add", *items)

    def rm_files(self, *items: str | Path) -> None:
        to_remove = [item for item in items if Path(item).exists()]

        if to_remove:
            self.git_cmd("rm", *to_remove)
