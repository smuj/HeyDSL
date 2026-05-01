# HeyDSL

HeyDSL is a lightweight local web UI for editing custom DSLs with live HTML preview.

If you've built a domain-specific language that produces visual output (diagrams,
formatted text, HTML, or graphics), HeyDSL gives you an interactive editor to develop
and test it.

Give HeyDSL a preview function, a compile function, and syntax highlighting rules, and
it provides:
- Live preview as you type
- Syntax highlighting for your DSL
- Compile & save output to disk

It's designed for local development and can be deployed in your own applications.

## Installation

```bash
pip install heydsl
```

## Quick Start

```python
from heydsl import DSLDefinition, HeyDSLApp, Syntax, LineCommentStyle

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

## Features

- Live preview: See output as you edit with no refresh needed
- Custom syntax highlighting: Built-in support for CodeMirror 5; define your syntax
highlighting rules via keyword lists or custom JavaScript
- Compile & save: Built-in file dialogs for saving output, or bring your own handlers
- Zero setup: Single Python app instance is the entire server
- Customizable UI: Swap editor themes, header text, and assets
- Local-first: Runs on `localhost` by default; deploy with your app if needed

## Configuration

### Defining Syntax

Create syntax highlighting in two ways:

From keyword/type/operator lists:
```python
syntax = Syntax.from_lists(
    name="MyDSL",
    keywords=["if", "else", "for", "return"],
    types=["int", "string", "bool"],
    operators=["+", "-", "*", "/", "=", "=="],
    line_comment_style=LineCommentStyle.HASH,
)
```

From a custom CodeMirror 5 mode file:
```python
syntax = Syntax.from_file("MyDSL", Path("my_mode.js"))
```

If creating from a file, make sure the name matches the mode name within the file.

### Customizing the UI

```python
from heydsl import UIConfig, curated_cm5_themes

ui = UIConfig(
    header_text="My DSL Editor",
    code_themes=curated_cm5_themes(),  # or provide your own
)

app = HeyDSLApp(dsl_definition, ui_config=ui)
```

### Save Handlers

By default, saving opens a file dialog. You can customize this:

```python
from heydsl import save_file, save_compiled
from datetime import datetime

def custom_save(code: str) -> str:
    """Custom save handler with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Use the built-in helper
    return save_file(code, default_name=f"my_dsl_{timestamp}.dsl")

def custom_compile_save(compiled: bytes) -> str:
    """Custom compiled save handler with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Use the built-in helper
    return save_compiled(compiled, default_name=f"output_{timestamp}.bin")

app = HeyDSLApp(
    DSLDefinition(
        syntax=my_syntax,
        preview_fn=my_preview_fn,
        compile_fn=my_compile_fn,
        save_fn=custom_save,
        save_compiled_fn=custom_compile_save,
    )
)
```

Or skip the dialogs entirely:

```python
def save_to_disk(code: str) -> str:
    path = Path("/tmp/dsl_output.txt")
    path.write_text(code)
    return str(path)

app = HeyDSLApp(
    DSLDefinition(
        syntax=my_syntax,
        preview_fn=my_preview_fn,
        compile_fn=my_compile_fn,
        save_fn=save_to_disk,
    )
)
```

## HTML Preview & Security

The `clean_preview` setting controls how preview HTML is handled.

When `clean_preview=True` (default):
- Preview HTML is sanitized: only safe tags and attributes are allowed
- Content Security Policy is restrictive: no scripts, forms, or external requests
- Useful as a safety check while developing

When `clean_preview=False`:
- Preview HTML is rendered as-is
- CSP is permissive: scripts and forms can run
- It is your responsibility to ensure preview output is safe

For local development tools with trusted input, disabling is normal:

```python
app = HeyDSLApp(
    DSLDefinition(
        syntax=my_syntax,
        preview_fn=my_preview_fn,
        compile_fn=my_compile_fn,
        clean_preview=False,  # You control the preview output
    )
)
```

If you're running in a shared environment or accepting untrusted DSL code without
sanitising it, keep it enabled.

## Deploying HeyDSL

HeyDSL runs as a Flask app. You can:

- Use the built-in `run()` method for development
- Integrate with any WSGI server (Gunicorn, uWSGI) for production
- Embed in a larger Flask/FastAPI application via the `.app` attribute

```python
# Get the Flask app for WSGI deployment
flask_app = heydsl_app.app
```

---

# API Reference

## Core Classes

### `DSLDefinition`
Configuration for your DSL. All fields except noted optional are required.

| Field | Type | Description |
|-------|------|-------------|
| `syntax` | `Syntax` | Syntax definition for editor highlighting |
| `preview_fn` | `Callable[[str], str]` | Function that converts code to HTML preview |
| `compile_fn` | `Callable[[str], bytes]` | Function that compiles code to output |
| `save_fn` | `Callable[[str], str]` | (Optional) Custom save handler; defaults to file dialog |
| `save_compiled_fn` | `Callable[[bytes], str]` | (Optional) Custom compiled save handler; defaults to file dialog |
| `initial_file` | `Path \| None` | (Optional) File to load on startup |
| `sample_code` | `str` | (Optional) Code shown when no file is loaded |
| `clean_preview` | `bool` | (Optional) Enable HTML sanitization and strict CSP; default `True` |

### `HeyDSLApp`
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
- `run(open_browser: bool = True)` - Start the server and optionally open in browser

**Attributes:**
- `app` - The underlying Flask application object

### `Syntax`
Defines syntax highlighting rules.

**Class Methods:**
- `from_lists(name, line_comment_style, keywords, types=[], operators=[])` - Create from keyword/type/operator lists
- `from_file(name, path)` - Load syntax definition from a JavaScript file

**Attributes:**
- `name` - Display name for the syntax
- `definition` - CodeMirror 5 mode JavaScript code

### `LineCommentStyle`
Enum for comment syntax. Values: `SLASH_SLASH` (`//`), `HASH` (`#`), `SEMI` (`;`), `PERCENT` (`%`), `NONE` (disabled)

### `ServerConfig`
Server settings.

```python
ServerConfig(
    host: str = "127.0.0.1",
    port: int = 5000,
)
```

**Methods:**
- `address()` - Return the full `http://host:port` address

### `UIConfig`
UI customization.

```python
UIConfig(
    header_text: str = "HeyDSL Editor",
    code_themes: dict[str, ExternalAsset] = curated_cm5_themes(),
)
```

### `ExternalAsset`
External stylesheet or script to load.

```python
ExternalAsset(
    type: AssetType,  # AssetType.STYLESHEET or AssetType.SCRIPT
    url: str,
    integrity: str | None = None,  # SRI hash
)
```

### `AssetType`
Enum for asset types: `STYLESHEET`, `SCRIPT`

## Utilities

### `save_file(code, default_name="code.txt", initial_dir=None, filetypes=None) -> str`
Opens a save dialog and writes code to the selected file. Returns the file path. Use within custom `save_fn` handlers.

### `save_compiled(compiled_bytes, default_name="output.bin", initial_dir=None, filetypes=None) -> str`
Opens a save dialog and writes compiled bytes to the selected file. Returns the file path. Use within custom `save_compiled_fn` handlers.

### `curated_cm5_themes() -> dict[str, ExternalAsset]`
Returns popular CodeMirror 5 themes: cobalt, dracula, eclipse, material, monokai, solarized.

### `default_cm5_assets() -> list[ExternalAsset]`
Returns CodeMirror 5 core and simple mode assets.

## HTTP API

The Flask app exposes these endpoints (for advanced use):

- `GET /` - Main editor UI
- `GET /syntax-def.js` - CodeMirror syntax definition
- `POST /api/preview` - Generate preview (JSON request: `{"code": "..."}`)
- `POST /api/compile` - Compile and save (JSON request: `{"code": "..."}`)
- `POST /api/save-as` - Save code (JSON request: `{"code": "..."}`)
