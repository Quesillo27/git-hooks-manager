"""Shim legacy — preserva la API original usada en README y tests smoke.

Todo apunta al paquete `hookman/`. Se mantiene para no romper integraciones
que usan:
    python git_hooks_manager.py install all
"""

import sys
from pathlib import Path
from types import SimpleNamespace

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from hookman.hooks.builtins import BUILTIN_HOOKS  # noqa: E402
from hookman.utils import (  # noqa: E402
    find_git_root,
    get_hooks_dir,
    is_executable,
    make_executable,
)
from hookman.commands.install_cmd import install_one  # noqa: E402


HOOKS = {
    "pre-commit": BUILTIN_HOOKS["pre-commit/no-secrets"]["content"],
    "commit-msg": BUILTIN_HOOKS["commit-msg/conventional"]["content"],
    "pre-push": BUILTIN_HOOKS["pre-push/run-tests"]["content"],
}

HOOKS_LIBRARY = BUILTIN_HOOKS


def install_hook(git_root: Path, hook_name: str, force: bool = False) -> bool:
    """Instala un hook simple por tipo (pre-commit|commit-msg|pre-push).

    Mantiene la firma histórica: recibe el root del repo y el nombre del hook.
    """
    if hook_name not in HOOKS:
        print(
            f"Hook '{hook_name}' no conocido. Disponibles: {', '.join(HOOKS.keys())}"
        )
        return False

    mapping = {
        "pre-commit": "pre-commit/no-secrets",
        "commit-msg": "commit-msg/conventional",
        "pre-push": "pre-push/run-tests",
    }
    ok, msg = install_one(mapping[hook_name], git_root, force=force)
    print(msg)
    return ok


def remove_hook(git_root: Path, hook_name: str) -> bool:
    """Elimina un hook por nombre de tipo."""
    hook_path = get_hooks_dir(git_root) / hook_name
    if hook_path.exists():
        hook_path.unlink()
        print(f"Hook '{hook_name}' eliminado")
        return True
    print(f"Hook '{hook_name}' no encontrado")
    return False


def list_hooks(git_root: Path) -> None:
    """Lista los hooks instalados (legacy format)."""
    hooks_dir = get_hooks_dir(git_root)
    print(f"\nHooks en {hooks_dir}:\n")
    installed = []
    for name in HOOKS:
        path = hooks_dir / name
        status = "instalado" if path.exists() else "no instalado"
        print(f"  {name:<15} {status}")
        if path.exists():
            installed.append(name)
    print(f"\nTotal: {len(installed)}/{len(HOOKS)} hooks instalados")


def install_all(git_root: Path, force: bool = False) -> None:
    """Instala los 3 hooks clásicos."""
    print(f"Instalando todos los hooks en {git_root}...")
    count = sum(install_hook(git_root, h, force) for h in HOOKS)
    print(f"\n{count}/{len(HOOKS)} hooks instalados")


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Git Hooks Manager — Instala y gestiona git hooks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python git_hooks_manager.py install all
  python git_hooks_manager.py install pre-commit
  python git_hooks_manager.py install pre-commit --force
  python git_hooks_manager.py remove commit-msg
  python git_hooks_manager.py list
""",
    )
    parser.add_argument("--path", default=".", help="Ruta al repo")

    sub = parser.add_subparsers(dest="command", required=True)

    p_install = sub.add_parser("install")
    p_install.add_argument("hook")
    p_install.add_argument("--force", "-f", action="store_true")

    p_remove = sub.add_parser("remove")
    p_remove.add_argument("hook")

    sub.add_parser("list")

    args = parser.parse_args()
    search_path = Path(args.path)
    git_root = find_git_root(search_path)
    if not git_root:
        print(f"No se encontro repositorio git en '{search_path}' ni en sus padres")
        return 1
    print(f"Repo git: {git_root}")

    if args.command == "install":
        if args.hook == "all":
            install_all(git_root, args.force)
            return 0
        return 0 if install_hook(git_root, args.hook, args.force) else 1
    if args.command == "remove":
        return 0 if remove_hook(git_root, args.hook) else 1
    if args.command == "list":
        list_hooks(git_root)
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
