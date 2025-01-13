# Writing a Script

Use [uv] to create a script that depends on this library.

```
$ uv init --script mod.py
$ uv add --script mod.py modify-repos
```

Subclass {class}`.GitHubScript` to define the repositories to change and what
changes to make. This uses the [gh] GitHub CLI, which must already be installed
and logged in.

```python
from modify_repos import GitHubScript, GitHubRepo

class MyScript(GitHubScript):
    # title used in commit and PR
    title = "..."
    # description used in commit and PR
    body = "..."
    # branch to merge into, defaults to main
    target = "main"
    # branch to create and PR
    branch = "my-changes"
    # one or more users/orgs to clone repos from
    orgs = ["username"]

    def select_for_clone(self, repo: GitHubRepo) -> bool:
        # filter to only clone some of the available repos
        return repo.name in {"a", "b", "d"}

    def modify(self, repo: GitHubRepo) -> None:
        # make any changes, such as add/remove files, here
        ...

if __name__ == "__main__":
    MyScript().run()
```

Call `uv run mod.py`, and it will clone and modify all the selected repos. PRs
will not be created unless you use `MyScript(submit=True)` instead, so you can
develop and preview your changes first.

[uv]: https://docs.astral.sh/uv/
[gh]: https://cli.github.com/
