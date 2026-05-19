"""
Shared dataclasses and the LanguageAdapter protocol.

The dataclasses are the stable contract returned by every language adapter,
so analyze_file.py and downstream consumers do not branch on language. Some
fields are language-specific (decorators apply to Python/JS/TS, annotations
to Python/Java/TS); they remain optional strings so the shape stays uniform.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Protocol, runtime_checkable

__all__ = [
    "ParameterInfo",
    "FunctionInfo",
    "ClassInfo",
    "ImportInfo",
    "ExternalCallInfo",
    "ParseResult",
    "LanguageAdapter",
]


CallType = Literal["database", "network", "filesystem", "messaging", "ipc", "other"]


@dataclass
class ParameterInfo:
    name: str
    annotation: str | None = None
    default: str | None = None


@dataclass
class FunctionInfo:
    name: str
    parameters: list[ParameterInfo] = field(default_factory=list)
    return_annotation: str | None = None
    is_async: bool = False
    is_classmethod: bool = False
    is_staticmethod: bool = False
    is_property: bool = False
    # Visibility hint, populated by adapters that know (Java public/private,
    # JS/TS export, SQL CREATE vs CREATE OR REPLACE).
    visibility: str | None = None
    docstring: str | None = None
    line_number: int = 0


@dataclass
class ClassInfo:
    name: str
    bases: list[str] = field(default_factory=list)
    methods: list[FunctionInfo] = field(default_factory=list)
    class_variables: list[str] = field(default_factory=list)
    # Distinguish class / interface / enum / record / struct / trait.
    kind: str = "class"
    visibility: str | None = None
    docstring: str | None = None
    line_number: int = 0


@dataclass
class ImportInfo:
    module: str
    names: list[str] = field(default_factory=list)
    is_from_import: bool = False
    is_internal: bool = False


@dataclass
class ExternalCallInfo:
    call_type: CallType
    pattern: str
    line_number: int
    context: str


@dataclass
class ParseResult:
    file_path: str
    language: str = "unknown"
    classes: list[ClassInfo] = field(default_factory=list)
    functions: list[FunctionInfo] = field(default_factory=list)
    imports: list[ImportInfo] = field(default_factory=list)
    constants: list[str] = field(default_factory=list)
    external_calls: list[ExternalCallInfo] = field(default_factory=list)
    exported_symbols: list[str] = field(default_factory=list)
    # Free-form notes from the adapter, e.g. "parser=tree-sitter" or
    # "parser=regex-fallback", "syntax errors recovered". Useful for the CLI
    # report and for tests.
    notes: list[str] = field(default_factory=list)


@runtime_checkable
class LanguageAdapter(Protocol):
    """Each language module exposes a module-level `adapter` matching this."""

    language: str

    def parse(self, content: str, file_path: str) -> ParseResult:
        ...

    def count_imports(self, content: str) -> int:
        ...

    def strip_comments_and_blanks(self, content: str) -> int:
        """Return number of non-empty, non-comment lines."""
        ...

    def extract_comments(
        self, content: str
    ) -> list["CommentToken"]:
        """
        Return all comments in the file with their token info.

        See comments.CommentToken for the shape.
        """
        ...


# Forward import declared here so adapters can import the type from base.
from .comments import CommentToken  # noqa: E402  (placed after Protocol on purpose)

__all__.append("CommentToken")
