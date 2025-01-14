from __future__ import annotations

import typing as t
from functools import cached_property
from pathlib import Path
from shutil import which
from subprocess import CompletedProcess

from ..repo.git import GitRepo
from ..utils import run_cmd

if t.TYPE_CHECKING:
    from ..script.base import Script


class GitHubRepo(GitRepo):
    """Subclass this to define how to manipulate Git repositories. This extends
    the plain :class:`GitRepo` to clone and create PRs using the GitHub CLI.

    :param script: The script being run to modify this repo.
    :param org: The GitHub user/org that owns the repo.
    :param name: The GitHub repo name.
    """

    _gh_exe: str | None = which("gh")
    direct_submit: bool = False
    """Whether to merge and push directly to the target branch, rather than
    creating a PR. This is disabled by default as a PR will give more
    opportunity to review any mistakes with the automated changes.
    """

    def __init__(self, script: Script[t.Any], org: str, name: str) -> None:
        self.org = org
        self.name = name
        super().__init__(script=script, remote_id=self.full_name)

    def gh_cmd(self, *args: str | Path) -> CompletedProcess[str]:
        """Call and pass args to the `gh` command.

        :param args: Command line arguments to the `gh` command.
        """
        if self._gh_exe is None:
            raise RuntimeError("GitHub CLI is not installed.")

        return run_cmd(self._gh_exe, *args)

    @cached_property
    def full_name(self) -> str:
        """The `org/name` identifier for the repo."""
        return f"{self.org}/{self.name}"

    def clone(self) -> None:
        self.local_dir.parent.mkdir(parents=True, exist_ok=True)
        self.gh_cmd(
            "repo",
            "clone",
            self.full_name,
            self.local_dir,
            "--",
            "-b",
            self.script.target,
        )

    def submit(self) -> None:
        if self.direct_submit:
            super().submit()
            return

        result = self.gh_cmd("pr", "view", "--json", "closed", "--jq", ".closed")
        has_pr = not result.returncode and result.stdout.strip() == "false"

        if not has_pr:
            self.git_cmd("push", "--set-upstream", "origin", self.script.branch)
            self.gh_cmd(
                "pr",
                "create",
                "--base",
                self.script.target,
                "--title",
                self.script.title,
                "--body",
                self.script.body,
            )
        else:
            # If open PR already exists from previous run, force push.
            self.git_cmd("push", "--force", "origin", self.script.branch)
