from __future__ import annotations

import typing as t
from contextlib import chdir
from functools import cached_property
from pathlib import Path

import click

if t.TYPE_CHECKING:
    from ..script.base import Script


class Repo:
    """Defines how to manipulate a repository. :meth:`.Script.list_repos` will
    return instances of a subclass of this that are set up to work with a
    specific type of repo, and most of the methods will be called as part of
    running the script. You'd subclass this class if you wanted to define such a
    class for a new type of repo.

    :param script: The script being run to modify this repo.
    :param remote_id: A value that identifies where this repo was cloned from.
    """

    remote_id: str

    def __init__(self, script: Script[t.Any], remote_id: str) -> None:
        self.script = script
        """The script being run to modify this repo."""

        self.remote_id = remote_id
        """A value that identifies where this repo was cloned from. The format
        depends on how the script finds repos.
        """

    @cached_property
    def local_dir(self) -> Path:
        """The path where this repo is cloned."""
        return self.script.clones_dir / self.remote_id

    def clone(self) -> None:
        """Clone the repository unconditionally. This is called by
        :meth:`clone_if_needed`.
        """
        raise NotImplementedError

    def clone_if_needed(self) -> None:
        """Clone the repository if the local directory doesn't exist. Calls
        :meth:`clone`. Called by :meth:`run`.
        """
        if not self.local_dir.exists():
            self.clone()

    def reset_target(self) -> None:
        """Reset the base branch that will be branched off of and merged into.
        This should ensure the repository is clean and up to date, discarding
        any changes from previous unsuccessful runs. Called by :meth:`run`.
        """
        raise NotImplementedError

    def reset_branch(self) -> None:
        """Create or reset the work branch. This should ensure the branch is
        freshly created from the target branch. Called by :meth:`run`.
        """
        raise NotImplementedError

    def needs_commit(self) -> bool:
        """Check if there are uncommitted changes. Called by
        :meth:`auto_commit_if_needed`.
        """
        raise NotImplementedError

    def auto_commit(self) -> None:
        """Create a commit unconditionally. This is called by
        :meth:`auto_commit_if_needed` to create the automatic commit when there
        are uncommitted changes, and should add those changes to the commit. It
        should not be called to create other intermediate commits. It should use
        :attr:`.Script.message` as the commit message.
        """
        raise NotImplementedError

    def auto_commit_if_needed(self) -> None:
        """Create a commit if there are uncommitted changes. Calls
        :meth:`needs_commit` and :meth:`auto_commit_if_needed`. Called by
        :meth:`run`.
        """
        if self.needs_commit():
            self.auto_commit()

    def needs_submit(self) -> bool:
        """Check if there are commits that have not been pushed upstream. Called
        by :meth:`submit_if_needed`."""
        raise NotImplementedError

    def submit(self) -> None:
        """Submit the changes upstream. What this means depends on the
        implementation; whether it merges, creates a PR, or something else.
        """
        raise NotImplementedError

    def submit_if_needed(self) -> None:
        """Submit the changes if there are any changes. Is disabled by default
        by :attr:`.Script.enable_submit`, to prevent accidental submission of a
        script in development. Calls :meth:`needs_submit` and :meth:`submit`.
        Called by :meth:`run`.
        """
        if self.script.enable_submit and self.needs_submit():
            self.submit()
        else:
            click.secho("skipping submit", fg="yellow")

    def run(self) -> None:
        """Run the full workflow for this repo: clone, reset, modify, commit,
        submit. Calls many of the other methods defined in this class. Called
        by :meth:`.Script.run`.
        """
        click.secho(self.remote_id, fg="green")
        self.clone_if_needed()

        with chdir(self.local_dir):
            self.reset_target()

            if not self.script.select_for_modify(self):
                click.secho("skipping modify", fg="yellow")
                return

            self.reset_branch()
            self.script.modify(self)
            self.auto_commit_if_needed()
            self.submit_if_needed()
