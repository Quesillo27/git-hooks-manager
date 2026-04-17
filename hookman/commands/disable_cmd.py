"""Comandos `hookman disable` y `hookman enable`.

Renombra el archivo del hook a `<name>.disabled` para preservarlo sin que git
lo ejecute, y lo vuelve a habilitar en `enable`.
"""

from pathlib import Path
from types import SimpleNamespace

from hookman.utils import find_git_root, get_hooks_dir, hook_type, make_executable


def cmd_disable(args: SimpleNamespace) -> int:
    """Deshabilita un hook sin eliminarlo (renombra a .disabled)."""
    repo = find_git_root(Path(getattr(args, "path", ".") or "."))
    if not repo:
        print("ERROR: no estás dentro de un repositorio git")
        return 1

    htype = hook_type(args.hook)
    hooks_dir = get_hooks_dir(repo)
    active = hooks_dir / htype
    disabled = hooks_dir / f"{htype}.disabled"

    if not active.exists():
        if disabled.exists():
            print(f"WARN: hook '{htype}' ya estaba deshabilitado")
            return 0
        print(f"ERROR: hook '{htype}' no está instalado")
        return 1

    if disabled.exists():
        disabled.unlink()
    active.rename(disabled)
    print(f"OK: hook '{htype}' deshabilitado")
    return 0


def cmd_enable(args: SimpleNamespace) -> int:
    """Reactiva un hook previamente deshabilitado."""
    repo = find_git_root(Path(getattr(args, "path", ".") or "."))
    if not repo:
        print("ERROR: no estás dentro de un repositorio git")
        return 1

    htype = hook_type(args.hook)
    hooks_dir = get_hooks_dir(repo)
    active = hooks_dir / htype
    disabled = hooks_dir / f"{htype}.disabled"

    if not disabled.exists():
        print(f"ERROR: no hay hook '{htype}.disabled' para reactivar")
        return 1

    if active.exists():
        active.unlink()
    disabled.rename(active)
    make_executable(active)
    print(f"OK: hook '{htype}' reactivado")
    return 0
