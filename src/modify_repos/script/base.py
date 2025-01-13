import inspect
import typing as t
from functools import cached_property
from os import PathLike
from pathlib import Path

import jinja2
import platformdirs

from ..repo.base import Repo
from ..utils import read_text
from ..utils import wrap_text


class Script[RepoType: Repo]:
    """Defines how to select repositories and modify them. Typically, you'll
    want to subclass a more specific class that is already set up to work with a
    remote host. You'd subclass this class if you wanted to define such a class
    for a new host.

    :param submit: Whether to submit the changes. This is disabled by default,
        to give you a chance to develop the changes first.
    """

    target: str = "main"
    """The name of the target branch to branch off of and merge into."""

    branch: str
    """The name of the work branch to create."""

    title: str
    """A short title describing the change. Used as the first line of the
    automatic commit, as well as the title of the PR. By convention, this should
    be at most 50 characters.
    """

    body: str
    """Additional description about the change. Used in the commit message
    after the title, separated by an empty line. Also used as the body of the
    PR. This will be re-wrapped to 72 characters to match convention.
    """

    def __init__(self, *, submit: bool = False) -> None:
        """ """
        source_file = inspect.getsourcefile(self.__class__)

        if source_file is None:
            raise RuntimeError("Could not determine script root.")

        self.root_dir: Path = Path(source_file).parent
        """The directory containing the running script. Used to reference
        resource files and templates.
        """

        self.jinja_env: jinja2.Environment = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.root_dir),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
        )
        """A Jinja environment configured to use :attr:`root_dir` as a template
        folder. See :meth:`render_template`.
        """

        self.clones_dir: Path = platformdirs.user_cache_path("modify-repos") / "clones"
        """Directory where repos are cloned to. Uses the appropriate user cache
        dir for the platform.
        """

        self.clones_dir.mkdir(parents=True, exist_ok=True)

        if not (ignore := self.clones_dir / ".gitignore").exists():
            ignore.write_text("*\n")

        self.body = wrap_text(self.body, width=72)
        self.enable_submit = submit
        """Whether to submit the changes. This is disabled by default, to give
        you a chance to develop the changes first. It is set from the `submit`
        param.
        """

    def render_template(self, name: str, /, **kwargs: t.Any) -> str:
        """Render the named template file with context. Uses :attr:`jinja_env`,
        which finds templates next to the script file.

        :param name: Template name to load.
        :param kwargs: Context to pass to the render call.
        """
        return self.jinja_env.get_template(name).render(**kwargs)

    def list_all_repos(self) -> list[RepoType]:
        """Get the list of all repos that may be cloned. Override this to
        define how to generate this list. Called by :meth:`list_repos`."""
        raise NotImplementedError

    def list_repos(self) -> list[RepoType]:
        """Get the filtered list of repos that will be cloned. Override
        :meth:`list_all_repos` and :meth:`select_for_clone` to control what is
        returned here. Called by :meth:`run`."""
        return [r for r in self.list_all_repos() if self.select_for_clone(r)]

    @cached_property
    def full_target(self) -> str:
        """The upstream target branch, which is :attr:`target` prefixed by
        `origin/`.
        """
        return f"origin/{self.target}"

    @cached_property
    def commit_message(self) -> str:
        """The message to use for the automatic commit in :meth:`commit`.
        Defaults to :attr:`title` and :attr:`body` separated by a blank line.
        """
        return f"{self.title}\n\n{self.body}"

    def select_for_clone(self, repo: Repo) -> bool:
        """Select what repos are returned by :meth:`list_repos`. Each repo from
        :meth:`list_all_repos` is passed, and will be used if this method returns
        true for it.

        For example, override this to return true if the repo name matches a set
        of names.

        :param repo: The repo to filter.
        """
        return True

    def select_for_modify(self, repo: Repo) -> bool:
        """Select whether :meth:`modify` will be called on the repo. Called by
        :meth:`run` while the current directory is the cloned repo dir.

        For example, override this to return false if the repo does not contain
        a file to be removed, or already contains a file to be added.

        :param repo: The repo to filter.
        """
        return True

    def modify(self, repo: Repo) -> None:
        """Perform modifications to the repo. Called by :meth:`run` while the
        current directory is the cloned repo dir.

        If this leaves uncommitted changes, :meth:`.Repo.commit_if_needed` will
        detect that and commit automatically. You can also add and commit
        manually to skip that behavior.

        :param repo: The repo to modify.
        """
        raise NotImplementedError

    def run(self) -> None:
        """Call :meth:`.Repo.run` for each selected repo."""
        for repo in self.list_repos():
            repo.run()

    def read_text(self, path: str | PathLike[str], strip: bool = True) -> str:
        """Read a text file, where `path` is relative to the script's directory
        :attr:`root_dir`. The file will be read as UTF-8.

        :param path: Path to file to read. Relative paths are relative to
            :attr:`root_dir`.
        :param strip: Strip leading and trailing empty spaces and lines. Enabled
            by default. The text is often formatted into an existing file, so
            stripping spaces makes working with it more predictable.
        """
        return read_text(self.root_dir / path, strip=strip)
