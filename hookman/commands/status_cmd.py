"""Comando `hookman status` — hooks instalados en el repo."""

import json
from pathlib import Path
from types import SimpleNamespace

from hookman.config import VALID_HOOKS
from hookman.utils import find_git_root, get_hooks_dir, is_executable


def _collect_status(git_root: Path) -> list:
    hooks_dir = get_hooks_dir(git_root)
    result = []
    for h in VALID_HOOKS:
        hook_file = hooks_dir / h
        disabled_file = hooks_dir / f"{h}.disabled"
        if hook_file.exists():
            result.append({
                "name": h,
                "state": "installed",
                "executable": is_executable(hook_file),
                "size": hook_file.stat().st_size,
            })
        elif disabled_file.exists():
            result.append({
                "name": h,
                "state": "disabled",
                "executable": False,
                "size": disabled_file.stat().st_size,
            })
    return result


def cmd_status(args: SimpleNamespace = None) -> int:
    """Imprime el estado de los hooks del repo."""
    path = Path(getattr(args, "path", ".") or ".") if args else Path(".")
    git_root = find_git_root(path)
    if not git_root:
        print("ERROR: no se encontró repositorio git")
        return 1

    data = _collect_status(git_root)

    if args and getattr(args, "json", False):
        print(json.dumps({"repo": str(git_root), "hooks": data}, indent=2, sort_keys=True))
        return 0

    print(f"\n  Hooks en: {git_root}")
    print("-" * 50)
    if not data:
        print("  (ningún hook instalado)")
    else:
        for h in data:
            if h["state"] == "installed":
                marker = "[OK]" if h["executable"] else "[X]  (sin exec)"
            else:
                marker = "[--]"
            print(f"  {marker} {h['name']:<25} {h['state']:<10} ({h['size']} bytes)")
    print()
    return 0
