from __future__ import annotations

import collections.abc as c
import os
import shlex
import subprocess
import typing as t
from contextlib import contextmanager
from pathlib import Path

import click

type CmdArg = str | Path


def run_cmd(*args: CmdArg, **kwargs: t.Any) -> subprocess.CompletedProcess[str]:
    echo_cmd(args)
    result: subprocess.CompletedProcess[str] = subprocess.run(
        args,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        **kwargs,
    )

    if output := result.stdout.strip():
        click.echo(output)

    return result


def echo_cmd(args: c.Iterable[CmdArg]) -> None:
    click.echo(f"$ {shlex.join(str(v) for v in args)}")


@contextmanager
def pushd(new: Path) -> c.Iterator[None]:
    current = Path.cwd()

    if current != new:
        echo_cmd(["pushd", os.fspath(new)])
        os.chdir(new)

    yield

    if current != new:
        echo_cmd(["popd"])
        os.chdir(current)


def git_add(*args: CmdArg) -> None:
    run_cmd("git", "add", *args)
