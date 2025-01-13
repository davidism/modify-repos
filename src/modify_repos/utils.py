from __future__ import annotations

import os
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
    """Wrapper around :meth:`subprocess.run`. Args are passed positionally
    rather than as a list. Stdout and stderr are combined, and use text mode.
    The initial command is echoed, and if the return code is not 0, the output
    and code are echoed.

    :param args: Command line arguments.
    :param kwargs: Other arguments passed to `subprocess.run`.
    """
    s_args = [os.fspath(v) if isinstance(v, PathLike) else v for v in args]
    click.echo(f"$ {shlex.join(s_args)}")
    result: subprocess.CompletedProcess[str] = subprocess.run(
        s_args,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        **kwargs,
    )

    if result.returncode:
        click.echo(result.stdout)
        click.secho(f"exited with code {result.returncode}", fg="red")

    return result


def wrap_text(text: str, width: int = 80) -> str:
    """Wrap a multi-line, multi-paragraph string. The text is dedented and empty
    spaces and lines are stripped, to support triple-quoted strings. Paragraphs
    are separated by a blank line `\\\\n\\\\n`. Tabs are converted to 4 spaces,
    and very long words are not wrapped.

    :param text: The text to process.
    :param width: The number of characters to wrap at.
    """
    return "\n\n".join(
        textwrap.fill(p, width=width, tabsize=4, break_long_words=False)
        for p in cleandoc(text).split("\n\n")
    )


def read_text(path: str | PathLike[str], strip: bool = True) -> str:
    """Read a file as UTF-8 text.

    :param path: The path to the file to read.
    :param strip: Whether to strip empty spaces and lines. Enabled by default.
        This makes the text more predictable to work with when inserting it into
        another text.
    """
    text = Path(path).read_text("utf8")

    if strip:
        text = text.strip()

    return text


def write_text(path: str | PathLike[str], text: str, end_nl: bool = True) -> None:
    """Write a file as UTF-8 text.

    :param path: The path to the file to write.
    :param text: The text to write.
    :param end_nl: Whether to ensure the text ends with exactly one newline
        `\\\\n`. This keeps file endings consistent.
    """
    if end_nl:
        text = f"{text.rstrip('\n')}\n"

    Path(path).write_text(text, "utf8")
