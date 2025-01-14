from shutil import which

from ..repo.github import GitHubRepo
from ..utils import run_cmd
from .base import Script


class GitHubScript(Script[GitHubRepo]):
    """Subclass this to define how to select and modify GitHub repositories.
    Uses the GitHub CLI, which must already be installed and logged in.

    :param submit: Whether to submit the changes. This is disabled by default,
        to give you a chance to develop the changes first.
    :param orgs: The list of users/orgs to clone repositories from.
    """

    orgs: list[str]
    """The list of GitHub users/orgs to clone repositories from."""

    def __init__(self, *, submit: bool = False, orgs: list[str] | None = None) -> None:
        super().__init__(submit=submit)

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
