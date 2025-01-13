# modify-repos

A framework for writing scripts that clone, modify, and create pull requests
across multiple repositories at once. Various utilities such as a Jinja template
environment and text manipulation are provided to make common script tasks
easier.

```{warning}
This is under development, and how it's used may change at any time.
```

Currently, only a GitHub provider is implemented. The library is designed to be
extended to define other sources and repository types.

Create a Python file, subclass {class}`.GitHubScript`, define a few attributes
and its {meth}`~.GitHubScript.modify` method, then call its
{meth}`~.GitHubScript.run` method. See {doc}`script` for a full example.

```{toctree}
:hidden:

script
providers/github
utils
providers/git
providers/base
changes
license
```
