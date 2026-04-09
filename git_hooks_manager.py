#!/usr/bin/env python3
"""Git Hooks Manager — Instala y gestiona git hooks en proyectos."""

import argparse
import os
import stat
import sys
from pathlib import Path

HOOKS = {
    "pre-commit": """#!/bin/bash
# Pre-commit hook: verifica syntax y linting
echo "Ejecutando pre-commit checks..."
if [ -f "package.json" ] && grep -q '"lint"' package.json; then
    npm run lint --silent || { echo "Lint fallo"; exit 1; }
fi
if find . -name "*.py" -not -path "./.git/*" -not -path "./node_modules/*" | head -1 | grep -q .; then
    python -m py_compile $(find . -name "*.py" -not -path "./.git/*" -not -path "./node_modules/*") 2>&1 || { echo "Syntax error en Python"; exit 1; }
fi
echo "Pre-commit OK"
exit 0
""",
    "commit-msg": """#!/bin/bash
# Commit-msg hook: valida formato del mensaje
MSG_FILE="$1"
MSG=$(cat "$MSG_FILE")
if [ ${#MSG} -lt 10 ]; then
    echo "Mensaje de commit muy corto (minimo 10 caracteres)"
    exit 1
fi
if echo "$MSG" | grep -q "^\\s"; then
    echo "El mensaje no debe empezar con espacio"
    exit 1
fi
echo "Commit message OK"
exit 0
""",
    "pre-push": """#!/bin/bash
# Pre-push hook: corre tests antes de push
echo "Ejecutando tests antes de push..."
if [ -f "package.json" ] && grep -q '"test"' package.json; then
    npm test --silent 2>&1 || { echo "Tests fallaron -- push cancelado"; exit 1; }
elif [ -f "Makefile" ] && grep -q "^test:" Makefile; then
    make test || { echo "Tests fallaron -- push cancelado"; exit 1; }
fi
echo "Pre-push OK"
exit 0
""",
}

def find_git_root(path):
    """Encuentra el directorio raiz del repo git."""
    current = path.resolve()
    while current != current.parent:
        if (current / ".git").is_dir():
            return current
        current = current.parent
    return None

def install_hook(git_root, hook_name, force=False):
    """Instala un hook en el repo."""
    hooks_dir = git_root / ".git" / "hooks"
    hooks_dir.mkdir(exist_ok=True)
    hook_path = hooks_dir / hook_name

    if hook_path.exists() and not force:
        print(f"Hook '{hook_name}' ya existe. Usa --force para sobrescribir.")
        return False

    hook_content = HOOKS.get(hook_name)
    if not hook_content:
        print(f"Hook '{hook_name}' no conocido. Disponibles: {', '.join(HOOKS.keys())}")
        return False

    hook_path.write_text(hook_content)
    hook_path.chmod(hook_path.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    print(f"Hook '{hook_name}' instalado en {hook_path}")
    return True

def remove_hook(git_root, hook_name):
    """Elimina un hook del repo."""
    hook_path = git_root / ".git" / "hooks" / hook_name
    if hook_path.exists():
        hook_path.unlink()
        print(f"Hook '{hook_name}' eliminado")
        return True
    print(f"Hook '{hook_name}' no encontrado")
    return False

def list_hooks(git_root):
    """Lista hooks instalados."""
    hooks_dir = git_root / ".git" / "hooks"
    print(f"\nHooks en {hooks_dir}:\n")
    installed = []
    for hook_name in HOOKS:
        path = hooks_dir / hook_name
        status = "instalado" if path.exists() else "no instalado"
        print(f"  {hook_name:<15} {status}")
        if path.exists():
            installed.append(hook_name)
    print(f"\nTotal: {len(installed)}/{len(HOOKS)} hooks instalados")

def install_all(git_root, force=False):
    """Instala todos los hooks disponibles."""
    print(f"Instalando todos los hooks en {git_root}...")
    count = sum(install_hook(git_root, h, force) for h in HOOKS)
    print(f"\n{count}/{len(HOOKS)} hooks instalados")

def main():
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
    parser.add_argument("--path", default=".", help="Ruta al repo (default: directorio actual)")

    subparsers = parser.add_subparsers(dest="command", required=True)

    install_parser = subparsers.add_parser("install", help="Instalar hook(s)")
    install_parser.add_argument("hook", help="Nombre del hook o 'all'")
    install_parser.add_argument("--force", "-f", action="store_true", help="Sobrescribir si existe")

    remove_parser = subparsers.add_parser("remove", help="Eliminar un hook")
    remove_parser.add_argument("hook", help="Nombre del hook")

    subparsers.add_parser("list", help="Listar hooks instalados")

    args = parser.parse_args()

    search_path = Path(args.path)
    git_root = find_git_root(search_path)
    if not git_root:
        print(f"No se encontro repositorio git en '{search_path}' ni en sus padres")
        sys.exit(1)
    print(f"Repo git: {git_root}")

    if args.command == "install":
        if args.hook == "all":
            install_all(git_root, args.force)
        else:
            success = install_hook(git_root, args.hook, args.force)
            sys.exit(0 if success else 1)
    elif args.command == "remove":
        success = remove_hook(git_root, args.hook)
        sys.exit(0 if success else 1)
    elif args.command == "list":
        list_hooks(git_root)

if __name__ == "__main__":
    main()
