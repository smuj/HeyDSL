"""Flask routes and application setup for HeyDSL"""

import webbrowser
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from threading import Timer

from flask import Flask, Response, jsonify, render_template, request

from .file_handler import save_compiled_dialog, save_file_dialog
from .asset import AssetType, ExternalAsset
from .clean_preview import sandbox, wrap_preview
from .cm5_assets import curated_cm5_themes, default_cm5_assets
from .syntax import Syntax


@dataclass(frozen=True)
class DSLDefinition:
    """Represents a complete DSL definition."""

    syntax: Syntax
    preview_fn: Callable[[str], str]
    compile_fn: Callable[[str], bytes]
    save_fn: Callable[[str], str] = lambda c: save_file_dialog(c)
    save_compiled_fn: Callable[[bytes], str] = lambda c: save_compiled_dialog(c)
    initial_file: Path | None = None  # Initial file to load on startup
    sample_code: str = ""
    clean_preview: bool = True


@dataclass(frozen=True)
class ServerConfig:
    """Represents the server configuration for HeyDSL."""

    host: str = "127.0.0.1"
    port: int = 5000

    def address(self) -> str:
        """Return the full address of the server."""
        return f"http://{self.host}:{self.port}"


@dataclass(frozen=True)
class UIConfig:
    """Represents UI configuration options for HeyDSL."""

    header_text: str = "HeyDSL Editor"
    code_themes: dict[str, ExternalAsset] = field(default_factory=curated_cm5_themes)


class HeyDSLApp:
    """Main application class for HeyDSL"""

    def __init__(
        self,
        dsl_definition: DSLDefinition,
        ui_config: UIConfig = UIConfig(),
        server_config: ServerConfig = ServerConfig(),
        cm5_assets: list[ExternalAsset] = default_cm5_assets(),
    ):
        self.dsl_definition = dsl_definition
        self.ui_config = ui_config
        self.server_definition = server_config

        self.assets: list[ExternalAsset] = cm5_assets + list(
            ui_config.code_themes.values()
        )

        # Load initial file content if provided
        if dsl_definition.initial_file:
            self.initial_code = dsl_definition.initial_file.read_text(encoding="utf-8")
        else:
            self.initial_code = dsl_definition.sample_code

        self.app = Flask(__name__, template_folder="templates", static_folder="static")
        self._register_routes()

    def _register_routes(self):
        @self.app.route("/")
        def index():
            return render_template(
                "editor.html",
                syntax_name=self.dsl_definition.syntax.name,
                initial_code=self.initial_code,
                sandbox=sandbox(self.dsl_definition.clean_preview),
                header_text=self.ui_config.header_text,
                stylesheets=[
                    asset for asset in self.assets if asset.type == AssetType.STYLESHEET
                ],
                scripts=[
                    asset for asset in self.assets if asset.type == AssetType.SCRIPT
                ],
                theme_names=list(self.ui_config.code_themes.keys()),
            )

        @self.app.route("/syntax-def.js")
        def syntax_def():
            return Response(
                self.dsl_definition.syntax.definition, mimetype="application/javascript"
            )

        @self.app.route("/api/preview", methods=["POST"])
        def preview():
            data = request.get_json()
            if not data or "code" not in data:
                return jsonify({"error": "Missing 'code' field in request"}), 400
            try:
                html = wrap_preview(
                    self.dsl_definition.preview_fn(data["code"]),
                    clean=self.dsl_definition.clean_preview,
                )
                return jsonify({"html": html})
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/compile", methods=["POST"])
        def compile():
            """Compile code and save result using user-supplied save function."""
            data = request.get_json()
            if not data or "code" not in data:
                return jsonify({"error": "Missing 'code' field in request"}), 400
            try:
                compiled = self.dsl_definition.compile_fn(data["code"])
                path = self.dsl_definition.save_compiled_fn(compiled)
                return jsonify({"success": True, "path": path})
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route("/api/save-as", methods=["POST"])
        def save_as():
            """Save code using user-supplied save function."""
            # Expected JSON: {"code": "code content"}
            data = request.get_json()
            if not data or "code" not in data:
                return jsonify({"error": "Missing 'code' field"}), 400

            try:
                path = self.dsl_definition.save_fn(data["code"])
                return jsonify({"success": True, "path": path})
            except Exception as e:
                return jsonify({"error": str(e)}), 500

    def run(self, open_browser: bool = True) -> None:
        """Run the Flask app and open it in the default web browser."""
        if open_browser:
            Timer(1, lambda: webbrowser.open(self.server_definition.address())).start()
        self.app.run(self.server_definition.host, self.server_definition.port)
