from __future__ import annotations

import dataclasses
from functools import cached_property
from inspect import isclass
from pathlib import Path
from pkgutil import resolve_name

from modify_repos.cmd import echo_cmd
from modify_repos.cmd import pushd
from modify_repos.cmd import run_cmd


@dataclasses.dataclass
class Repo:
    org: str
    name: str
    dir: Path

    @cached_property
    def full_name(self) -> str:
        return f"{self.org}/{self.name}"

    def clone(self, script: Script) -> None:
        self.dir.parent.mkdir(parents=True, exist_ok=True)

        if self.dir.exists():
            with pushd(self.dir):
                run_cmd("git", "switch", "-f", script.target)
                run_cmd("git", "pull", "--prune")
        else:
            run_cmd(
                "gh",
                "repo",
                "clone",
                f"{self.org}/{self.name}",
                self.dir,
                "--",
                "-b",
                script.target,
            )

    def modify(self, script: Script) -> None:
        run_cmd(
            "git",
            "switch",
            "--no-track",
            "-C",
            script.branch,
            f"origin/{script.target}",
        )
        script.modify(self)

        if run_cmd("git", "status", "--porcelain"):
            run_cmd("git", "add", "--all")
            run_cmd("git", "commit", "--message", f"{script.title}\n\n{script.body}")

    def push(self, script: Script) -> None:
        if not script.push:
            return

        echo_cmd(
            [
                "git",
                "push",
                "--set-upstream",
                "origin",
                script.branch,
            ]
        )
        echo_cmd(
            [
                "gh",
                "pr",
                "create",
                "--base",
                script.target,
                "--title",
                script.title,
                "--body",
                script.body,
            ]
        )


class Script:
    title: str
    body: str
    target: str = "main"
    branch: str

    def __init__(self, orgs: list[str], push: bool) -> None:
        self.clones_dir: Path = Path("clones")
        self.orgs = orgs
        self.push = push

    @classmethod
    def load_cls(cls, name: str) -> type[Script]:
        obj = resolve_name(name)

        if isclass(obj) and obj is not Script and issubclass(obj, Script):
            return obj

        for val in vars(obj).values():
            if isclass(val) and val is not Script and issubclass(val, Script):
                return val

        raise RuntimeError(f"Could not load script {name!r}.")

    def list_repos(self) -> list[Repo]:
        return [
            Repo(org, name, self.clones_dir / org / name)
            for org in self.orgs
            for name in run_cmd(
                "gh",
                "repo",
                "list",
                "--no-archived",
                "--json",
                "name",
                "--jq",
                ".[] | .name",
                org,
            ).stdout.splitlines()
        ]

    def run(self) -> None:
        self.clones_dir.mkdir(exist_ok=True)
        ignore = self.clones_dir / ".gitignore"

        if not ignore.exists():
            ignore.write_text("*\n")

        for repo in self.list_repos():
            if self.select_for_clone(repo):
                repo.clone(self)

                if self.select_for_modify(repo):
                    with pushd(repo.dir):
                        repo.modify(self)
                        repo.push(self)

    def select_for_clone(self, repo: Repo) -> bool:
        return True

    def select_for_modify(self, repo: Repo) -> bool:
        return True

    def modify(self, repo: Repo) -> None:
        raise NotImplementedError
