"""Helpers for canonicalizing product identifiers."""

import re
import unicodedata
from typing import Any


def canonicalize_string(value: str | Any) -> str:
    """Return a lowercase, ASCII-only key for the provided string."""

    if value in (None, ""):
        return ""

    decoded = str(value)
    normalized = unicodedata.normalize("NFKD", decoded)
    without_accents = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    cleaned = re.sub(r"[^a-z0-9]+", "", without_accents.lower())
    return cleaned or without_accents.lower()


__all__ = ["canonicalize_string"]
