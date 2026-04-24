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
