import nh3

_PERMITTED_TAGS = {
    # Text structure
    "p",
    "br",
    "hr",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    # Inline formatting
    "b",
    "strong",
    "i",
    "em",
    "u",
    "s",
    "sub",
    "sup",
    "span",
    "code",
    "kbd",
    # Lists
    "ul",
    "ol",
    "li",
    # Block elements
    "div",
    "blockquote",
    "pre",
    # Tables
    "table",
    "thead",
    "tbody",
    "tfoot",
    "tr",
    "th",
    "td",
    # Media
    "img",
    # Links
    "a",
}

_PERMITTED_ATTRIBUTES = {
    "*": {"class", "style"},
    "a": {"href", "title", "target"},
    "img": {"src", "alt", "title", "width", "height"},
    "table": {"border", "cellpadding", "cellspacing"},
    "th": {"colspan", "rowspan"},
    "td": {"colspan", "rowspan"},
}

_PERMITTED_CSS = {
    # Text
    "color",
    "background-color",
    "font-family",
    "font-size",
    "font-weight",
    "font-style",
    "text-align",
    "text-decoration",
    "white-space",
    # Spacing
    "margin",
    "margin-left",
    "margin-right",
    "margin-top",
    "margin-bottom",
    "padding",
    "padding-left",
    "padding-right",
    "padding-top",
    "padding-bottom",
    # Borders
    "border",
    "border-width",
    "border-style",
    "border-color",
    "border-radius",
    # Layout (safe subset)
    "display",
    "vertical-align",
    # Tables
    "border-collapse",
}
_PERMITTED_URL_SCHEMES = {"http", "https", "mailto"}


def html_clean(html: str) -> str:
    """Sanitize HTML using nh3 with a generous but safe allow-list."""
    return nh3.clean(
        html,
        tags=_PERMITTED_TAGS,
        attributes=_PERMITTED_ATTRIBUTES,
        url_schemes=_PERMITTED_URL_SCHEMES,
        filter_style_properties=_PERMITTED_CSS,
        strip_comments=True,
        link_rel="noopener noreferrer",
    )


_CSP_SAFE = (
    "default-src 'none'; "
    "img-src https: data:; "
    "style-src 'unsafe-inline'; "
    "font-src 'none'; "
    "media-src 'none'; "
    "frame-src 'none'; "
    "connect-src 'none'; "
    "object-src 'none'; "
    "base-uri 'none'; "
    "form-action 'none';"
)

_CSP_UNSAFE = (
    "default-src * data: blob:; "
    "script-src * 'unsafe-inline' 'unsafe-eval' data: blob:; "
    "img-src * data: blob:; "
    "style-src * 'unsafe-inline'; "
    "font-src * data:; "
    "media-src *; "
    "frame-src *; "
    "connect-src *; "
    "object-src 'none'; "
    "base-uri 'none';"
)

_SANDBOX_SAFE = "allow-popups"
_SANDBOX_UNSAFE = "allow-scripts allow-forms allow-popups allow-modals allow-downloads"


def wrap_preview(raw_fragment: str, clean: bool = True) -> str:
    """Wrap the raw HTML fragment in a full HTML document with CSP and optional cleaning."""
    fragment = html_clean(raw_fragment) if clean else raw_fragment
    csp = _CSP_SAFE if clean else _CSP_UNSAFE

    return (
        "<!DOCTYPE html>"
        "<html><head>"
        "<meta charset='utf-8'>"
        f"<meta http-equiv='Content-Security-Policy' content=\"{csp}\">"
        "<style>body{margin:0;padding:1rem;font-family:sans-serif;}</style>"
        "</head><body>"
        f"{fragment}"
        "</body></html>"
    )


def sandbox(clean: bool = True) -> str:
    """Return the sandbox attribute value for the iframe based on the clean flag."""
    return _SANDBOX_SAFE if clean else _SANDBOX_UNSAFE
