"""Comando `hookman uninstall`."""

from pathlib import Path
from types import SimpleNamespace

from hookman.logger import get_logger
from hookman.utils import find_git_root, get_hooks_dir, hook_type


def cmd_uninstall(args: SimpleNamespace) -> int:
    """Elimina un hook del repo actual."""
    repo_path = Path(getattr(args, "path", ".") or ".")
    git_root = find_git_root(repo_path)
    if not git_root:
        print("ERROR: no estás dentro de un repositorio git")
        return 1

    hooks_dir = get_hooks_dir(git_root)
    htype = hook_type(args.hook)
    hook_file = hooks_dir / htype

    if not hook_file.exists():
        disabled = hooks_dir / f"{htype}.disabled"
        if disabled.exists():
            disabled.unlink()
            print(f"OK: hook deshabilitado '{htype}' eliminado")
            return 0
        print(f"WARN: hook '{htype}' no estaba instalado")
        return 0

    if getattr(args, "dry_run", False):
        print(f"[dry-run] eliminaría {hook_file}")
        return 0

    hook_file.unlink()
    get_logger().info("uninstall hook=%s repo=%s", htype, git_root.name)
    print(f"OK: hook '{htype}' eliminado")
    return 0
