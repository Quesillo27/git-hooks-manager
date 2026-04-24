"""Utilidades reutilizables de hookman."""

import os
import stat
from pathlib import Path
from typing import Optional


def find_git_root(path: Optional[Path] = None) -> Optional[Path]:
    """Sube en el árbol de directorios hasta encontrar un .git/.

    Returns:
        Path absoluto al repo git, o None si no se encuentra.
    """
    p = (path or Path.cwd()).resolve()
    while p != p.parent:
        if (p / ".git").is_dir() or (p / ".git").is_file():
            return p
        p = p.parent
    if (p / ".git").exists():
        return p
    return None


def get_hooks_dir(repo_path: Path) -> Path:
    """Devuelve el directorio de hooks real del repo.

    Soporta repos normales (`.git/` directorio) y worktrees/submódulos donde
    `.git` es un archivo con `gitdir: ...`.
    """
    git_ref = repo_path / ".git"
    if git_ref.is_dir():
        return git_ref / "hooks"

    if git_ref.is_file():
        content = git_ref.read_text().strip()
        prefix = "gitdir:"
        if content.lower().startswith(prefix):
            git_dir = content[len(prefix):].strip()
            return (repo_path / git_dir).resolve() / "hooks"

    return git_ref / "hooks"


def make_executable(path: Path) -> None:
    """Agrega permisos de ejecución al archivo (user/group/other)."""
    current = path.stat().st_mode
    path.chmod(current | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)


def is_executable(path: Path) -> bool:
    """Verdadero si el archivo es ejecutable por el usuario."""
    return path.exists() and os.access(path, os.X_OK)


def hook_type(name: str) -> str:
    """Extrae el tipo de hook del nombre completo.

    Ejemplos:
        "pre-commit/no-secrets" → "pre-commit"
        "pre-commit"            → "pre-commit"
    """
    return name.split("/", 1)[0]


def hook_short_name(name: str) -> str:
    """Extrae la segunda parte del nombre, o el nombre completo si no tiene `/`."""
    parts = name.split("/", 1)
    return parts[1] if len(parts) > 1 else parts[0]
