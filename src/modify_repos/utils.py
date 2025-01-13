from __future__ import annotations

import shlex
import subprocess
import textwrap
import typing as t
from inspect import cleandoc
from os import PathLike
from pathlib import Path

import click


def run_cmd(
    *args: str | PathLike[str], **kwargs: t.Any
) -> subprocess.CompletedProcess[str]:
    echo_cmd(*args)
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


def echo_cmd(*args: str | PathLike[str]) -> None:
    click.echo(f"$ {shlex.join(str(v) for v in args)}")


def wrap_text(text: str, width: int = 80) -> str:
    """Wrap a multi-line, multi-paragraph string."""
    return "\n\n".join(
        textwrap.fill(p, width=width, tabsize=4, break_long_words=False)
        for p in cleandoc(text).split("\n\n")
    )


def read_text(path: str | PathLike[str], strip: bool = True) -> str:
    text = Path(path).read_text("utf8")

    if strip:
        text = text.strip()

    return text


def write_text(path: str | PathLike[str], text: str, end_nl: bool = True) -> None:
    if end_nl:
        text = f"{text.rstrip('\n')}\n"

    Path(path).write_text(text, "utf8")
