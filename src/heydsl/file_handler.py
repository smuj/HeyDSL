"""Tkinter file dialog functions for save/compile operations."""

from pathlib import Path

import tkinter as tk
import tkinter.filedialog as filedialog


def _save_dialog(
    default_name: str = "file.txt",
    initial_dir: str | None = None,
    filetypes: list[tuple[str, str]] | None = None,
    title: str = "Save File",
) -> Path:
    """Show a save dialog and save code to file.

    Args:
        code: Content to save
        initial_dir: Initial directory for dialog (optional)
        default_name: Default filename for the save dialog
        filetypes: List of (description, pattern) tuples for file type filter

    Returns:
        Path to saved file

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
            "title": title,
            "defaultextension": Path(default_name).suffix,
            "initialfile": default_name,
            "filetypes": filetypes,
        }

        if initial_dir:
            kwargs["initialdir"] = initial_dir

        path = filedialog.asksaveasfilename(parent=root, **kwargs)
        if not path:
            raise Exception("Save cancelled by user")

        return Path(path)
    finally:
        root.destroy()


def save_file(
    code: str,
    default_name: str = "code.txt",
    initial_dir: str | None = None,
    filetypes: list[tuple[str, str]] | None = None,
) -> str:
    """Save code using a file dialog."""
    path = _save_dialog(
        default_name=default_name,
        initial_dir=initial_dir,
        filetypes=filetypes,
        title="Save code",
    )
    path.write_text(code, encoding="utf-8")
    return str(path)


def save_compiled(
    compiled_bytes: bytes,
    default_name: str = "output.bin",
    initial_dir: str | None = None,
    filetypes: list[tuple[str, str]] | None = None,
) -> str:
    """Save compiled bytes using a file dialog."""
    path = _save_dialog(
        default_name=default_name,
        initial_dir=initial_dir,
        filetypes=filetypes,
        title="Save compiled output",
    )
    path.write_bytes(compiled_bytes)
    return str(path)
