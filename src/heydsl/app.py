"""Flask routes and application setup for HeyDSL"""

import io
import webbrowser
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from threading import Timer
from typing import Self

from flask import Flask, Response, jsonify, render_template, request, send_file


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


class HeyDSLApp:
    """Main application class for HeyDSL"""

    def __init__(
        self,
        compile_fn: Callable[[str], bytes],
        preview_fn: Callable[[str], str],
        syntax: Syntax,
        compiled_filename_fn: Callable[[], str] = lambda: "output.bin",
        initial_code="",
        host="127.0.0.1",
        port=5000,
    ):
        self.compile_fn = compile_fn
        self.preview_fn = preview_fn
        self.compiled_filename_fn = compiled_filename_fn
        self.syntax = syntax
        self.initial_code = initial_code
        self.host = host
        self.port = port

        self.app = Flask(__name__, template_folder="templates", static_folder="static")
        self._register_routes()

    def _register_routes(self):
        @self.app.route("/")
        def index():
            return render_template(
                "editor.html",
                syntax_name=self.syntax.name,
                initial_code=self.initial_code,
            )

        @self.app.route("/syntax-def.js")
        def syntax_def():
            return Response(self.syntax.definition, mimetype="application/javascript")

        @self.app.route("/api/preview", methods=["POST"])
        def preview():
            data = request.get_json()
            if not data or "code" not in data:
                return jsonify({"error": "Missing 'code' field in request"}), 400
            try:
                html = self.preview_fn(data["code"])
                return jsonify({"html": html})
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/compile", methods=["POST"])
        def compile():
            data = request.get_json()
            if not data or "code" not in data:
                return jsonify({"error": "Missing 'code' field in request"}), 400
            try:
                output = self.compile_fn(data["code"])

                return send_file(
                    io.BytesIO(output),
                    mimetype="application/octet-stream",
                    as_attachment=True,
                    download_name=self.compiled_filename_fn(),
                )
            except Exception as e:
                return jsonify({"error": str(e)}), 500

    def run(self, open_browser: bool = True) -> None:
        """Run the Flask app and open it in the default web browser."""
        if open_browser:
            Timer(1, lambda: webbrowser.open(f"http://{self.host}:{self.port}")).start()
        self.app.run(port=self.port, host=self.host, debug=True, use_reloader=False)
