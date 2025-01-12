from __future__ import annotations

import os
import sys

import click

from modify_repos.models import Script


@click.command
@click.option("-s", "--script", "script_name", required=True)
@click.option("--push/--no-push")
def cli(script_name: str, push: bool) -> None:
    script_cls = Script.load_cls(script_name)
    script = script_cls(push)
    script.run()


def entry_point() -> None:
    sys.path.insert(0, os.getcwd())
    cli()
