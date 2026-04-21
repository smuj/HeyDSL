"""Flask routes and application setup for HeyDSL"""

from pathlib import Path

from flask import Flask, Response, jsonify, render_template, request


def register_routes(app):
    """Register URL routes for the Flask application"""

    @app.route("/")
    def index():
        """Render the main editor page"""
        return render_template(
            "editor.html",
            syntax_name=app.syntax_name,
            initial_code=app.initial_code,
        )

    @app.route("/syntax-def.js")
    def syntax_def():
        """Serve the syntax definition JS file"""
        return Response(app.syntax_def, mimetype="application/javascript")

    @app.route("/api/preview", methods=["POST"])
    def preview():
        """Generate preview HTML from code.

        Expected request JSON: {"code": "..."}
        Returns JSON: {"html": "..."} or {"error": "..."}
        """
        if not app.preview_fn:
            return jsonify({"error": "No preview function configured"}), 400

        data = request.get_json()
        if not data or "code" not in data:
            return jsonify({"error": "Missing 'code' field in request"}), 400

        code = data["code"]

        try:
            html = app.preview_fn(code)
            return jsonify({"html": html})
        except Exception as e:
            return jsonify({"error": str(e)}), 500


def create_app(compile_fn, preview_fn, syntax_def_path, syntax_name, initial_code=""):
    """Create and configure the application.

    Args:
        compile_fn: Callable for compiling code.
        preview_fn: Callable that takes code (str) and returns HTML (str).
                   Called to generate live preview from editor content.
        syntax_def_path: Path to a JS file to serve as the DSL syntax mode.
        syntax name: The name of the syntax (e.g. "python", "dsl").
        initial_code: Initial code to display in the editor. Defaults to empty string.

    Returns:
        Flask application instance
    """
    from .app import register_routes

    app = Flask(__name__, template_folder="templates", static_folder="static")

    # Store configuration on app for routes to access
    app.compile_fn = compile_fn
    app.preview_fn = preview_fn
    app.syntax_name = syntax_name
    app.initial_code = initial_code

    src = Path(syntax_def_path)
    if src.exists():
        app.syntax_def = src.read_text(encoding="utf-8")
    else:
        raise FileNotFoundError(f"DSL mode file not found: {syntax_def_path}")

    # Register routes
    register_routes(app)

    return app
