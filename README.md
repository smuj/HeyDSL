# HeyDSL

A lightweight local web UI for editing custom DSLs with live HTML preview. HeyDSL provides a minimalist editor interface with syntax highlighting, live previewing, and code compilation—perfect for developing and testing domain-specific languages.

## Installation

```bash
pip install heydsl
```

## Quick Start

```python
from heydsl import *

def preview_fn(code: str) -> str:
    """Convert DSL to HTML for preview"""
    return f"<pre>{code}</pre>"

def compile_fn(code: str) -> bytes:
    """Compile DSL to output format"""
    return code.encode()

app = HeyDSLApp(
    DSLDefinition(
        syntax=Syntax.from_lists(
            name="MyDSL",
            keywords=["if", "else", "function"],
            line_comment_style=LineCommentStyle.HASH,
        ),
        preview_fn=preview_fn,
        compile_fn=compile_fn,
        sample_code="# Hello World",
    )
)
app.run()
```

Visit `http://127.0.0.1:5000` in your browser to start editing.

## API Reference

### Core Classes

#### `DSLDefinition`
Configuration for your DSL. All fields except noted optional are required.

| Field | Type | Description |
|-------|------|-------------|
| `syntax` | `Syntax` | Syntax definition for editor highlighting |
| `preview_fn` | `Callable[[str], str]` | Function that converts code to HTML preview |
| `compile_fn` | `Callable[[str], bytes]` | Function that compiles code to output |
| `save_fn` | `Callable[[str], str]` | (Optional) Custom save handler; defaults to temp file |
| `save_compiled_fn` | `Callable[[bytes], str]` | (Optional) Custom compiled save handler |
| `initial_file` | `Path \| None` | (Optional) File to load on startup |
| `sample_code` | `str` | (Optional) Code shown when no file is loaded |
| `clean_preview` | `bool` | (Optional) Enable HTML sanitization and strict CSP; default `True` |

#### `HeyDSLApp`
Main application class.

```python
HeyDSLApp(
    dsl_definition: DSLDefinition,
    ui_config: UIConfig = UIConfig(),
    server_config: ServerConfig = ServerConfig(),
    cm5_assets: list[ExternalAsset] = default_cm5_assets(),
)
```

**Methods:**
- `run(open_browser: bool = True)` — Start the server and optionally open in browser

#### `Syntax`
Defines syntax highlighting rules.

**Class Methods:**
- `from_lists(name, line_comment_style, keywords, types=[], operators=[])` — Create from keyword/type/operator lists
- `from_file(name, path)` — Load syntax definition from a JavaScript file

**Attributes:**
- `name` — Display name for the syntax
- `definition` — CodeMirror 5 mode JavaScript code

#### `LineCommentStyle`
Enum for comment syntax. Values: `SLASH_SLASH` (`//`), `HASH` (`#`), `SEMI` (`;`), `PERCENT` (`%`), `NONE` (disabled)

#### `ServerConfig`
Server settings.

```python
ServerConfig(
    host: str = "127.0.0.1",
    port: int = 5000,
)
```

#### `UIConfig`
UI customization.

```python
UIConfig(
    header_text: str = "HeyDSL Editor",
    code_themes: dict[str, ExternalAsset] = curated_cm5_themes(),
)
```

#### `ExternalAsset`
External stylesheet or script to load.

```python
ExternalAsset(
    type: AssetType,  # AssetType.STYLESHEET or AssetType.SCRIPT
    url: str,
    integrity: str | None = None,  # SRI hash
)
```

### Utilities

#### `curated_cm5_themes() -> dict[str, ExternalAsset]`
Returns popular CodeMirror 5 themes: cobalt, dracula, eclipse, material, monokai, solarized.

#### `default_cm5_assets() -> list[ExternalAsset]`
Returns CodeMirror 5 core and simple mode assets.

## The `clean_preview` Toggle

The `clean_preview` setting controls security and HTML sanitization in the preview panel.

### When `clean_preview=True` (default)

- **HTML Sanitization**: Preview HTML is cleaned using an allowlist. Only safe tags (p, div, img, table, etc.) and attributes are permitted. JavaScript-enabling tags and attributes are stripped.
- **Content Security Policy**: Strict CSP disallows scripts, forms, and dangerous operations. Only images and styling are permitted.
- **Iframe Sandbox**: Limited permissions (`allow-popups` only)—no scripts or forms can execute.

**Best practice:** Keep this enabled unless you're certain preview output is trusted.

### When `clean_preview=False`

- **Raw HTML**: Preview HTML is passed through unmodified. Dangerous content is not filtered.
- **Permissive CSP**: Allows scripts, forms, and cross-origin requests.
- **Iframe Sandbox**: Full permissions—scripts and forms can execute.

**When it's safe to disable:**
- You control all DSL input (no user-provided code)
- The preview function is a trusted internal tool
- You're running in an isolated local environment with no network exposure

**When to leave it on:**
- Any untrusted or user-provided DSL code
- Production systems or shared environments
- When preview output could include external/dynamic content

### Example

```python
# Strict security for user-submitted DSL
app1 = HeyDSLApp(DSLDefinition(
    syntax=syntax,
    preview_fn=preview,
    compile_fn=compile,
    clean_preview=True,  # Default, but explicit for clarity
))

# Internal development tool (trusted environment)
app2 = HeyDSLApp(DSLDefinition(
    syntax=syntax,
    preview_fn=preview,
    compile_fn=compile,
    clean_preview=False,  # Only if you trust the preview output completely
))
```

## API Endpoints

The Flask app exposes these HTTP endpoints (for advanced use):

- `GET /` — Main editor UI
- `GET /syntax-def.js` — CodeMirror syntax definition
- `POST /api/preview` — Preview generated HTML (JSON: `{"code": "..."}`)
- `POST /api/compile` — Compile and save (JSON: `{"code": "..."}`)
- `POST /api/save-as` — Save code (JSON: `{"code": "..."}`)
