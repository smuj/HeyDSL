import json
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Self, Sequence


class LineCommentStyle(Enum):
    SLASH_SLASH = "//"
    HASH = "#"
    SEMI = ";"
    PERCENT = "%"
    NONE = ""  # disables line comments


_STRING_RE = r'"(?:[^\\]|\\.)*?(?:"|$)"'
_NUMBER_RE = r"[-+]?(?:\d*\.\d+|\d+)\b"
_IDENTIFIER_RE = r"[a-zA-Z_][\w-]*"
_WHITESPACE_RE = r"\s+"
_DEFAULT_TYPES = tuple()
_DEFAULT_OPERATORS = (
    "+",
    "-",
    "*",
    "/",
    "%",
    "=",
    "==",
    "!=",
    "<",
    ">",
    "<=",
    ">=",
    "&&",
    "||",
    ":",
)

_CM5_SIMPLE_MODE_TEMPLATE = """(function(mod) {{
  if (typeof exports == "object" && typeof module == "object")
    mod(require("codemirror"));
  else if (typeof define == "function" && define.amd)
    define(["codemirror"], mod);
  else
    mod(window.CodeMirror);
}})(function(CodeMirror) {{
  "use strict";

  CodeMirror.defineSimpleMode("{name}", {{
    start: [
{start_block}
    ]{meta_block}
  }});
}});
"""


def _js_escape(s: str) -> str:
    """Escape a Python string for safe insertion inside a JavaScript regex literal."""
    if not s:
        return s
    # Use re.escape then ensure forward slash is escaped for JS regex literal
    escaped = re.escape(s).replace("/", r"\/")
    # Also escape literal newlines and carriage returns
    return escaped.replace("\n", r"\n").replace("\r", r"\r")


def _words_to_regex(words: Sequence[str]) -> str:
    escaped = [_js_escape(w) for w in (x.strip() for x in words) if w]
    return r"\b(?:" + "|".join(escaped) + r")\b" if escaped else ""


def _ops_to_regex(ops: Sequence[str]) -> str:
    cleaned = [o for o in (x.strip() for x in ops) if o]
    if not cleaned:
        return ""
    # prefer longest first so multi-char ops match before prefixes
    escaped = [_js_escape(o) for o in sorted(cleaned, key=len, reverse=True)]
    return r"(?:" + "|".join(escaped) + r")"


def _line_comment_regex(style: LineCommentStyle) -> str:
    s = style.value
    return _js_escape(s) + r".*" if s else r"(?!x)x"


def _sanitise_name(name: str) -> str:
    """Produce a safe lowercase token for both mode id and mime suffix."""
    n = name.strip().lower().replace(" ", "-")
    n = re.sub(r"[^a-z0-9_-]", "", n)
    return n or "mydsl"


@dataclass(frozen=True)
class Syntax:
    """Represents a syntax definition for the editor"""

    name: str
    definition: str

    @classmethod
    def from_file(cls, name: str, path: Path) -> Self:
        """Create a Syntax instance from a file"""
        if not path.exists():
            raise FileNotFoundError(f"Syntax definition file not found: {path}")
        definition = path.read_text(encoding="utf-8")
        return cls(name=name, definition=definition)

    @classmethod
    def from_lists(
        cls,
        name: str,
        line_comment_style: LineCommentStyle,
        keywords: Sequence[str],
        types: Sequence[str] = _DEFAULT_TYPES,
        operators: Sequence[str] = _DEFAULT_OPERATORS,
    ) -> Self:
        """Create a Syntax instance from lists of syntax elements.

        Args:
            name (str): The name of the syntax/mode.
            line_comment_style (LineCommentStyle): The style of line comments.
            keywords (Sequence[str]): A list of keywords to highlight.
            types (Sequence[str]): A list of types to highlight.
            operators (Sequence[str]): A list of operators to highlight.

        Returns:
        A string containing the JavaScript code for the CodeMirror mode.
        """
        name = _sanitise_name(name)

        parts = []
        parts.append(f' {{regex: /{_STRING_RE}/, token: "string"}}')
        parts.append(
            f' {{regex: /{_line_comment_regex(line_comment_style)}/, token: "comment"}}'
        )

        kw_re = _words_to_regex(keywords)
        if kw_re:
            parts.append(f' {{regex: /{kw_re}/, token: "keyword"}}')

        types_re = _words_to_regex(types)
        if types_re:
            parts.append(f' {{regex: /{types_re}/, token: "atom"}}')

        parts.append(f' {{regex: /{_NUMBER_RE}/, token: "number"}}')

        ops_re = _ops_to_regex(operators)
        if ops_re:
            parts.append(f' {{regex: /{ops_re}/, token: "operator"}}')

        parts.append(f' {{regex: /{_IDENTIFIER_RE}/, token: "variable"}}')
        parts.append(f" {{regex: /{_WHITESPACE_RE}/, token: null}}")

        start_block = ",\n".join(parts)
        meta_line = line_comment_style.value
        meta_block = (
            f",\n    meta: {{\n      lineComment: {json.dumps(meta_line)}\n    }}"
            if meta_line
            else ""
        )

        definition = _CM5_SIMPLE_MODE_TEMPLATE.format(
            name=name, start_block=start_block, meta_block=meta_block
        )

        return cls(name=name, definition=definition)
