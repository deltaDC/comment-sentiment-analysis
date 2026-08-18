"""Input text validation for predict endpoint."""

from __future__ import annotations

import unicodedata

INVALID_TEXT_MSG = (
    "Text contains invalid characters. Use letters, numbers, and basic punctuation only."
)

_ALLOWED_PUNCT = frozenset(".,?!:;'\"()-")


def text_has_invalid_chars(text: str) -> bool:
    for ch in text:
        if ch.isspace() or ch in _ALLOWED_PUNCT or ch.isdigit():
            continue
        if unicodedata.category(ch).startswith("L"):
            continue
        return True
    return False


if __name__ == "__main__":
    assert not text_has_invalid_chars("VF3 giá tốt, đi phố tiện!")
    assert text_has_invalid_chars("hello@world")
    assert text_has_invalid_chars("price #1")
    assert text_has_invalid_chars("cost $100")
