"""
Optional tree-sitter loader.

Returns a (parser, language) pair or None if tree-sitter or the requested
grammar is unavailable. Adapters call this and fall back to regex parsing
when it returns None.

We prefer `tree-sitter-language-pack` (modern, single dependency, bundles
many grammars) and fall back to per-grammar packages
(`tree-sitter-python`, `tree-sitter-java`, etc.) if the user has installed
those directly.
"""

from __future__ import annotations

import functools
from typing import Any

__all__ = ["get_parser", "TreeSitterUnavailable"]


class TreeSitterUnavailable(RuntimeError):
    """Raised internally when tree-sitter can't be loaded for a language."""


# Aliases used by tree-sitter-language-pack.
_LANG_PACK_ALIASES = {
    "python": "python",
    "java": "java",
    "javascript": "javascript",
    "typescript": "typescript",
    "tsx": "tsx",
    "sql": "sql",
}


@functools.lru_cache(maxsize=None)
def get_parser(language: str) -> tuple[Any, Any] | None:
    """
    Return (parser, language_obj) for the requested language, or None if
    tree-sitter is not installed or the grammar is unavailable.
    """
    pack_name = _LANG_PACK_ALIASES.get(language)
    if pack_name is None:
        return None

    # Strategy 1: tree-sitter-language-pack (preferred).
    try:
        from tree_sitter_language_pack import get_parser as _ts_get_parser  # type: ignore
        from tree_sitter_language_pack import get_language as _ts_get_lang  # type: ignore

        parser = _ts_get_parser(pack_name)
        lang_obj = _ts_get_lang(pack_name)
        return parser, lang_obj
    except Exception:
        pass

    # Strategy 2: tree-sitter-languages (older bundled package).
    try:
        from tree_sitter_languages import get_parser as _ts_get_parser  # type: ignore
        from tree_sitter_languages import get_language as _ts_get_lang  # type: ignore

        parser = _ts_get_parser(pack_name)
        lang_obj = _ts_get_lang(pack_name)
        return parser, lang_obj
    except Exception:
        pass

    # Strategy 3: individual tree-sitter-<lang> + tree-sitter core.
    try:
        from tree_sitter import Language, Parser  # type: ignore

        # Map our canonical names to import names.
        import_name = {
            "python": "tree_sitter_python",
            "java": "tree_sitter_java",
            "javascript": "tree_sitter_javascript",
            "typescript": "tree_sitter_typescript",
            "tsx": "tree_sitter_typescript",
            "sql": "tree_sitter_sql",
        }.get(pack_name)
        if import_name is None:
            return None
        mod = __import__(import_name)
        # tree-sitter-typescript exposes both language_typescript and language_tsx.
        if pack_name == "typescript":
            lang_capsule = mod.language_typescript()
        elif pack_name == "tsx":
            lang_capsule = mod.language_tsx()
        else:
            lang_capsule = mod.language()
        lang_obj = Language(lang_capsule)
        parser = Parser(lang_obj)
        return parser, lang_obj
    except Exception:
        return None


def node_text(node: Any, source_bytes: bytes) -> str:
    """Return the source text covered by a tree-sitter node."""
    try:
        return source_bytes[node.start_byte : node.end_byte].decode("utf-8", errors="replace")
    except Exception:
        return ""
