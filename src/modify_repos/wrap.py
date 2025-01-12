from __future__ import annotations

import textwrap
from inspect import cleandoc


def wrap(text: str, width: int = 80) -> str:
    """Wrap a multi-line, multi-paragraph string."""
    return "\n\n".join(
        textwrap.fill(p, width=width, tabsize=4, break_long_words=False)
        for p in cleandoc(text).split("\n\n")
    )
