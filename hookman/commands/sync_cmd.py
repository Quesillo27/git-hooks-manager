"""Comando `hookman sync` — copia hooks entre dos repos."""

import shutil
from pathlib import Path
from types import SimpleNamespace

from hookman.config import VALID_HOOKS
from hookman.utils import find_git_root, get_hooks_dir, make_executable


def cmd_sync(args: SimpleNamespace) -> int:
    """Copia los hooks instalados del repo fuente al destino."""
    src_root = find_git_root(Path(args.source))
    dst_root = find_git_root(Path(args.destination))

    if not src_root:
        print(f"ERROR: fuente no es un repo git: {args.source}")
        return 1
    if not dst_root:
        print(f"ERROR: destino no es un repo git: {args.destination}")
        return 1

    src_hooks = get_hooks_dir(src_root)
    dst_hooks = get_hooks_dir(dst_root)
    dst_hooks.mkdir(parents=True, exist_ok=True)

    copied = 0
    for h in VALID_HOOKS:
        src_file = src_hooks / h
        if src_file.exists() and not src_file.name.endswith(".sample"):
            dst_file = dst_hooks / h
            shutil.copy2(src_file, dst_file)
            make_executable(dst_file)
            copied += 1

    print(f"OK: {copied} hook(s) sincronizados de {src_root.name} → {dst_root.name}")
    return 0
