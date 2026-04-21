"""Flask routes and application setup for HeyDSL"""

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Self

from flask import Flask, Response, jsonify, render_template, request


@dataclass
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


def create_app(
    compile_fn: Callable[[str], Any],
    preview_fn: Callable[[str], str],
    syntax: Syntax,
    initial_code="",
) -> Flask:
    """Create and configure the application.

    Args:
        compile_fn: Callable that takes code (str) and returns compiled output.
        preview_fn: Callable that takes code (str) and returns HTML (str).
                   Called to generate live preview from editor content.
        syntax: Syntax highlighting rules for the editor.
        initial_code: Initial code to display in the editor. Defaults to empty string.
    """

    app = Flask(__name__, template_folder="templates", static_folder="static")

    # Register routes
    @app.route("/")
    def index():
        """Render the main editor page."""
        return render_template(
            "editor.html",
            syntax_name=syntax.name,
            initial_code=initial_code,
        )

    @app.route("/syntax-def.js")
    def syntax_def():
        """Serve the syntax definition JS."""
        return Response(syntax.definition, mimetype="application/javascript")

    @app.route("/api/preview", methods=["POST"])
    def preview():
        """Generate preview HTML from code.

        Expected request JSON: {"code": "..."}
        Returns JSON: {"html": "..."} or {"error": "..."}
        """
        data = request.get_json()
        if not data or "code" not in data:
            return jsonify({"error": "Missing 'code' field in request"}), 400

        try:
            html = preview_fn(data["code"])
            return jsonify({"html": html})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return app
