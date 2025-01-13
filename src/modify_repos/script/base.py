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
    target: str = "main"
    branch: str
    title: str
    body: str

    def __init__(self, *, submit: bool = False) -> None:
        source_file = inspect.getsourcefile(self.__class__)

        if source_file is None:
            raise RuntimeError("Could not determine script root.")

        self.root_dir: Path = Path(source_file).parent
        self.jinja_env: jinja2.Environment = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.root_dir),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
        )
        self.clones_dir: Path = platformdirs.user_cache_path("modify-repos") / "clones"
        self.clones_dir.mkdir(parents=True, exist_ok=True)

        if not (ignore := self.clones_dir / ".gitignore").exists():
            ignore.write_text("*\n")

        self.body = wrap_text(self.body, width=72)
        self.enable_submit = submit

    def render_template(self, name: str, /, **kwargs: t.Any) -> str:
        return self.jinja_env.get_template(name).render(**kwargs)

    def list_all_repos(self) -> list[RepoType]:
        raise NotImplementedError

    def list_repos(self) -> list[RepoType]:
        return [r for r in self.list_all_repos() if self.select_for_clone(r)]

    @cached_property
    def full_target(self) -> str:
        return f"origin/{self.target}"

    @cached_property
    def commit_message(self) -> str:
        return f"{self.title}\n\n{self.body}"

    def select_for_clone(self, repo: Repo) -> bool:
        return True

    def select_for_modify(self, repo: Repo) -> bool:
        return True

    def modify(self, repo: Repo) -> None:
        raise NotImplementedError

    def run(self) -> None:
        for repo in self.list_repos():
            repo.run()

    def read_text(self, path: str | PathLike[str], strip: bool = True) -> str:
        return read_text(self.root_dir / path, strip=strip)
