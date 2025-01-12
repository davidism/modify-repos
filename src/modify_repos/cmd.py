from __future__ import annotations

import collections.abc as c
import shlex
import subprocess
import typing as t
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

    if result.returncode:
        click.echo(result.stdout)
        click.secho(f"exited with code {result.returncode}", fg="red")

    return result


def echo_cmd(args: c.Iterable[CmdArg]) -> None:
    click.echo(f"$ {shlex.join(str(v) for v in args)}")
