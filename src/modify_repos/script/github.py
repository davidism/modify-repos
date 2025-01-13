from shutil import which

from ..repo.github import GitHubRepo
from ..utils import run_cmd
from .base import Script


class GitHubScript(Script[GitHubRepo]):
    def __init__(self, orgs: list[str] | None = None) -> None:
        super().__init__()

        if orgs is not None:
            self.orgs = orgs

    def list_all_repos(self) -> list[GitHubRepo]:
        return [
            GitHubRepo(self, org, name)
            for org in self.orgs
            for name in run_cmd(
                which("gh"),  # type: ignore[arg-type]
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
