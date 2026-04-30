"""Tkinter file dialog functions for save/compile operations."""

from pathlib import Path

import tkinter as tk
import tkinter.filedialog as filedialog


def save_file_dialog(
    code: str,
    initial_dir: str | None = None,
    default_extension: str = ".txt",
    filetypes: list[tuple[str, str]] | None = None,
) -> str:
    """Show a save dialog and save code to file.

    Args:
        code: Content to save
        initial_dir: Initial directory for dialog (optional)
        default_extension: Default file extension (e.g., ".txt")
        filetypes: List of (description, pattern) tuples for file type filter

    Returns:
        Path to saved file (string)

    Raises:
        Exception: If user cancels or save fails
    """
    if filetypes is None:
        filetypes = [("Text files", "*.txt"), ("All files", "*.*")]

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    try:
        kwargs = {
            "title": "Save File",
            "defaultextension": default_extension,
            "filetypes": filetypes,
        }

        if initial_dir:
            kwargs["initialdir"] = initial_dir

        path = filedialog.asksaveasfilename(parent=root, **kwargs)
        if not path:
            raise Exception("Save cancelled by user")

        Path(path).write_text(code, encoding="utf-8")
        return path
    finally:
        root.destroy()


def save_compiled_dialog(
    compiled_bytes: bytes,
    default_name: str = "output.bin",
    initial_dir: str | None = None,
    filetypes: list[tuple[str, str]] | None = None,
) -> str:
    """Show a save dialog and save compiled bytes to file.

    Args:
        compiled_bytes: Compiled binary content to save
        default_name: Default filename for the save dialog
        initial_dir: Initial directory for dialog (optional)
        filetypes: List of (description, pattern) tuples for file type filter

    Returns:
        Path to saved file (string)

    Raises:
        Exception: If user cancels or save fails
    """
    if filetypes is None:
        filetypes = [("All files", "*.*")]

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    try:
        kwargs = {
            "title": "Save Compiled Output",
            "defaultextension": Path(default_name).suffix,
            "initialfile": default_name,
            "filetypes": filetypes,
        }

        if initial_dir:
            kwargs["initialdir"] = initial_dir

        path = filedialog.asksaveasfilename(parent=root, **kwargs)
        if not path:
            raise Exception("Save cancelled by user")

        Path(path).write_bytes(compiled_bytes)
        return path
    finally:
        root.destroy()
