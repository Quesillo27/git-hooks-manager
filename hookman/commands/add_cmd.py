"""Comando `hookman add` — agrega un script a la librería personalizada."""

import shutil
from pathlib import Path
from types import SimpleNamespace

from hookman.config import HOOKS_LIBRARY, VALID_HOOKS
from hookman.utils import make_executable


def cmd_add_to_library(args: SimpleNamespace) -> int:
    """Copia un script de hook a ~/.hookman/library/<type>/<name>.sh."""
    src = Path(args.file)
    if not src.exists():
        print(f"ERROR: archivo '{args.file}' no encontrado")
        return 1

    htype = getattr(args, "type", None) or "pre-commit"
    if htype not in VALID_HOOKS:
        print(f"ERROR: tipo de hook inválido: {htype}")
        print(f"  Tipos válidos: {', '.join(VALID_HOOKS)}")
        return 1

    content = src.read_text()
    if not content.startswith("#!"):
        print("ERROR: el script debe empezar con shebang (#!/bin/bash)")
        return 1

    dest_name = getattr(args, "name", None) or src.stem
    dest_dir = HOOKS_LIBRARY / htype
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"{dest_name}.sh"

    shutil.copy2(src, dest)
    make_executable(dest)
    print(f"OK: hook '{htype}/{dest_name}' agregado a la librería")
    return 0
