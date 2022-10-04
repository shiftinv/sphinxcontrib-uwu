from __future__ import annotations

import random
import re
from typing import Any

from docutils import nodes
from docutils.writers._html_base import HTMLTranslator as BaseTranslator
from sphinx.application import Sphinx
from sphinx.writers.html import HTMLTranslator

__version__ = "0.0.1"


_map = [
    (re.compile(expr), res)
    for expr, res in [
        (r"[lr]", "w"),
        (r"[RL]", "W"),
        (r"n([aeiou])", r"ny\1"),
        (r"N([aeiou])", r"Ny\1"),
        (r"ove", "uv"),
    ]
]


def uwuify(text: str) -> str:
    # replace stuff
    for regex, res in _map:
        text = regex.sub(res, text)

    # add stutters
    words = text.split(" ")
    for i, word in enumerate(words):
        if not word or not word[0].isalpha():
            continue
        if random.random() > 0.05:
            continue
        word = (f"{word[0]}-" * random.randrange(1, 3)) + word
        words[i] = word

    return " ".join(words)


def create_translator(base: type[BaseTranslator]) -> type[BaseTranslator]:
    class UwuHTMLTranslator(base):
        def visit_Text(self, node: nodes.Text) -> None:
            if getattr(self, "protect_literal_text", None):
                return super().visit_Text(node)

            # intentionally not unescaping since the
            # node needs to be reconstructed later
            text = str(node)

            text = uwuify(text)

            # this loses other attached node data like the document,
            # but I hope no translator needs that
            return super().visit_Text(nodes.Text(text))

    return UwuHTMLTranslator


def setup(app: Sphinx) -> dict[str, Any]:
    # inherit old translator if possible (yay)
    old_translator = app.registry.translators.get("html") or HTMLTranslator
    assert issubclass(old_translator, BaseTranslator)
    translator_type = create_translator(old_translator)
    app.set_translator("html", translator_type, override=True)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
