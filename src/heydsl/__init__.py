"""HeyDSL - A lightweight local web UI for editing custom DSLs with live HTML preview"""

from .app import Syntax, create_app

__all__ = ["create_app", "Syntax"]
