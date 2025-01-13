from __future__ import annotations

import typing as t
from contextlib import chdir
from functools import cached_property
from pathlib import Path

import click

if t.TYPE_CHECKING:
    from ..script.base import Script


class Repo:
    remote_id: str

    def __init__(self, script: Script[t.Any], remote_id: str) -> None:
        self.script = script
        self.remote_id = remote_id

    @cached_property
    def local_dir(self) -> Path:
        return self.script.clones_dir / self.remote_id

    def clone(self) -> None:
        raise NotImplementedError

    def clone_if_needed(self) -> None:
        if not self.local_dir.exists():
            self.clone()

    def reset_target(self) -> None:
        raise NotImplementedError

    def reset_branch(self) -> None:
        raise NotImplementedError

    def needs_commit(self) -> bool:
        raise NotImplementedError

    def commit(self) -> None:
        raise NotImplementedError

    def commit_if_needed(self) -> None:
        if self.needs_commit():
            self.commit()

    def needs_submit(self) -> bool:
        raise NotImplementedError

    def submit(self) -> None:
        raise NotImplementedError

    def submit_if_needed(self) -> None:
        if self.script.enable_submit and self.needs_submit():
            self.submit()
        else:
            click.secho("skipping submit", fg="yellow")

    def run(self) -> None:
        click.secho(self.remote_id, fg="green")
        self.clone_if_needed()

        with chdir(self.local_dir):
            self.reset_target()

            if not self.script.select_for_modify(self):
                click.secho("skipping modify", fg="yellow")
                return

            self.reset_branch()
            self.script.modify(self)
            self.commit_if_needed()
            self.submit_if_needed()
