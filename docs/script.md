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

## Automatic Commit

After calling `modify`, the script will automatically add any tracked files
and create a commit if it detects there are uncommitted changes.

If you add a completely new file, it will not be tracked by Git yet, and this
won't be detected or committed. Therefore, you should call
{meth}`.Repo.add_files` to track any new files. Other modifications, such as
changing an existing file or using {meth}`.Repo.rm_files`, will already be
tracked by Git.

You can set {attr}`.GitRepo.add_untracked` to also detect and add completely
new untracked files. This is disabled by default as it might end up adding files
that were generated as a side effect of other changes.

```python
class MyScript(GitHubScript):
    def modify(self, repo: GitHubRepo) -> None:
        repo.add_untracked = True
        ...
```

## Merge vs PR

By default, the GitHub provider creates PRs. You can instruct a repo to merge
and push directly to the target instead. This is disabled by default because it
provides one less opportunity to ensure your script worked correctly.

Set {attr}`GitHubRepo.direct_submit` to `True` to enable this merge and push
behavior.

```python
class MyScript(GitHubScript):
    def modify(self, repo: GitHubRepo) -> None:
        repo.direct_submit = True
        ...
```

## Updating

You may have run your script with submit enabled, then noticed that more is
needed. If a branch and open PR already exist from a previous run of the script
that, a force push will be used to update.
