#!/usr/bin/env python3
"""
Git Hooks Manager — Instala y gestiona git hooks en proyectos de forma automática.
"""

import os
import sys
import stat
import json
import shutil
import argparse
from pathlib import Path
from typing import Optional

# ─── Hooks predefinidos ────────────────────────────────────────────────────────

HOOKS_LIBRARY = {
    "pre-commit": {
        "description": "Verifica sintaxis, linting y credenciales antes de commit",
        "content": """#!/bin/bash
# pre-commit hook — instalado por git-hooks-manager
set -e

echo "🔍 Ejecutando verificaciones pre-commit..."

# 1. Detectar credenciales hardcodeadas
PATTERNS="password\\s*=\\s*['\\\"][^'\\\"\\$]|secret\\s*=\\s*['\\\"][^'\\\"\\$]|api_key\\s*=\\s*['\\\"][^'\\\"\\$]"
if git diff --cached --name-only | xargs -I{} grep -lEi "$PATTERNS" {} 2>/dev/null | grep -qv ".example"; then
    echo "❌ Posibles credenciales detectadas en el commit. Revisar antes de continuar."
    exit 1
fi

# 2. Verificar sintaxis Python si hay archivos .py en el commit
PY_FILES=$(git diff --cached --name-only | grep '\\.py$' || true)
if [ -n "$PY_FILES" ]; then
    for f in $PY_FILES; do
        if [ -f "$f" ]; then
            python3 -m py_compile "$f" || { echo "❌ Error de sintaxis en $f"; exit 1; }
        fi
    done
    echo "✅ Sintaxis Python OK"
fi

# 3. Verificar sintaxis Node.js si hay archivos .js en el commit
JS_FILES=$(git diff --cached --name-only | grep '\\.js$' || true)
if [ -n "$JS_FILES" ] && command -v node &>/dev/null; then
    for f in $JS_FILES; do
        if [ -f "$f" ]; then
            node --check "$f" || { echo "❌ Error de sintaxis en $f"; exit 1; }
        fi
    done
    echo "✅ Sintaxis JS OK"
fi

echo "✅ Pre-commit checks pasados"
""",
    },
    "commit-msg": {
        "description": "Verifica formato del mensaje de commit (Conventional Commits)",
        "content": """#!/bin/bash
# commit-msg hook — instalado por git-hooks-manager
COMMIT_MSG=$(cat "$1")

# Verificar formato básico: tipo(scope): descripción
PATTERN="^(feat|fix|docs|style|refactor|test|chore|ci|perf|build)(\\(.+\\))?: .{1,72}$"

if ! echo "$COMMIT_MSG" | head -1 | grep -qE "$PATTERN"; then
    echo "❌ Mensaje de commit no sigue Conventional Commits."
    echo "   Formato: tipo(scope): descripción"
    echo "   Tipos válidos: feat, fix, docs, style, refactor, test, chore, ci, perf, build"
    echo "   Ejemplo: feat(auth): agregar login con Google"
    echo ""
    echo "   Tu mensaje: $COMMIT_MSG"
    exit 1
fi

echo "✅ Formato de commit OK"
""",
    },
    "pre-push": {
        "description": "Ejecuta tests antes de hacer push",
        "content": """#!/bin/bash
# pre-push hook — instalado por git-hooks-manager
set -e

echo "🧪 Ejecutando tests antes de push..."

# Node.js
if [ -f "package.json" ] && command -v npm &>/dev/null; then
    if grep -q '"test"' package.json; then
        npm test || { echo "❌ Tests fallaron. Push cancelado."; exit 1; }
    fi
fi

# Python
if [ -f "Makefile" ] && grep -q "^test:" Makefile; then
    make test || { echo "❌ Tests fallaron. Push cancelado."; exit 1; }
elif [ -f "pytest.ini" ] || [ -f "setup.py" ] || [ -f "pyproject.toml" ]; then
    python3 -m pytest --tb=short -q || { echo "❌ Tests fallaron. Push cancelado."; exit 1; }
fi

echo "✅ Tests pasados. Procediendo con push."
""",
    },
    "post-merge": {
        "description": "Instala dependencias automáticamente después de merge",
        "content": """#!/bin/bash
# post-merge hook — instalado por git-hooks-manager

changed_files() {
    git diff-tree -r --name-only --no-commit-id ORIG_HEAD HEAD
}

echo "🔄 Verificando cambios después del merge..."

# Reinstalar dependencias Node.js si cambió package.json
if changed_files | grep -q "package.json"; then
    echo "📦 package.json cambió — ejecutando npm install..."
    npm install
fi

# Reinstalar dependencias Python si cambió requirements.txt
if changed_files | grep -q "requirements.txt"; then
    echo "📦 requirements.txt cambió — ejecutando pip install..."
    pip install -r requirements.txt -q
fi

echo "✅ Post-merge completado"
""",
    },
}

# ─── Helpers ──────────────────────────────────────────────────────────────────


def find_git_root(start: Path) -> Optional[Path]:
    """Busca el directorio raíz del repo git desde start hacia arriba."""
    current = start.resolve()
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    return None


def get_hooks_dir(git_root: Path) -> Path:
    return git_root / ".git" / "hooks"


def make_executable(path: Path):
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def load_config(git_root: Path) -> dict:
    config_path = git_root / ".git-hooks.json"
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return {"installed": [], "disabled": []}


def save_config(git_root: Path, config: dict):
    config_path = git_root / ".git-hooks.json"
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)


# ─── Comandos ─────────────────────────────────────────────────────────────────


def cmd_list(args):
    """Lista hooks disponibles y cuáles están instalados."""
    git_root = find_git_root(Path(args.path or "."))
    if not git_root:
        print("❌ No estás en un repositorio git.")
        sys.exit(1)

    hooks_dir = get_hooks_dir(git_root)
    config = load_config(git_root)

    print(f"\n📂 Repo: {git_root}")
    print(f"🪝  Hooks dir: {hooks_dir}\n")
    print(f"{'Hook':<20} {'Estado':<12} Descripción")
    print("-" * 70)

    for name, info in HOOKS_LIBRARY.items():
        hook_path = hooks_dir / name
        installed = hook_path.exists() and name in config.get("installed", [])
        disabled = name in config.get("disabled", [])
        if disabled:
            status = "🔴 disabled"
        elif installed:
            status = "✅ installed"
        else:
            status = "⬜ available"
        print(f"{name:<20} {status:<12} {info['description']}")

    # Hooks custom en el dir que no son de la librería
    custom = [
        h.name
        for h in hooks_dir.iterdir()
        if h.is_file() and h.name not in HOOKS_LIBRARY and not h.name.endswith(".sample")
    ]
    if custom:
        print(f"\n{'─'*70}")
        print("Hooks custom instalados (no gestionados por este tool):")
        for name in custom:
            print(f"  • {name}")

    print()


def cmd_install(args):
    """Instala uno o más hooks en el repo."""
    git_root = find_git_root(Path(args.path or "."))
    if not git_root:
        print("❌ No estás en un repositorio git.")
        sys.exit(1)

    hooks_dir = get_hooks_dir(git_root)
    config = load_config(git_root)

    hooks_to_install = args.hooks if args.hooks else list(HOOKS_LIBRARY.keys())

    if args.all:
        hooks_to_install = list(HOOKS_LIBRARY.keys())

    installed_count = 0
    for hook_name in hooks_to_install:
        if hook_name not in HOOKS_LIBRARY:
            print(f"⚠️  Hook '{hook_name}' no encontrado en la librería. Saltando.")
            continue

        hook_path = hooks_dir / hook_name

        # Backup si ya existe
        if hook_path.exists() and not args.force:
            backup_path = hook_path.with_suffix(".backup")
            shutil.copy2(hook_path, backup_path)
            print(f"📋 Backup creado: {backup_path.name}")

        # Escribir hook
        hook_path.write_text(HOOKS_LIBRARY[hook_name]["content"])
        make_executable(hook_path)

        # Actualizar config
        if hook_name not in config.setdefault("installed", []):
            config["installed"].append(hook_name)
        if hook_name in config.get("disabled", []):
            config["disabled"].remove(hook_name)

        print(f"✅ Hook instalado: {hook_name}")
        installed_count += 1

    save_config(git_root, config)
    print(f"\n🎉 {installed_count} hook(s) instalado(s) en {git_root}")


def cmd_uninstall(args):
    """Desinstala uno o más hooks del repo."""
    git_root = find_git_root(Path(args.path or "."))
    if not git_root:
        print("❌ No estás en un repositorio git.")
        sys.exit(1)

    hooks_dir = get_hooks_dir(git_root)
    config = load_config(git_root)

    for hook_name in args.hooks:
        hook_path = hooks_dir / hook_name
        if hook_path.exists():
            hook_path.unlink()
            print(f"🗑️  Hook eliminado: {hook_name}")
        else:
            print(f"⚠️  Hook '{hook_name}' no estaba instalado.")

        if hook_name in config.get("installed", []):
            config["installed"].remove(hook_name)

    save_config(git_root, config)


def cmd_disable(args):
    """Deshabilita un hook renombrándolo a .disabled."""
    git_root = find_git_root(Path(args.path or "."))
    if not git_root:
        print("❌ No estás en un repositorio git.")
        sys.exit(1)

    hooks_dir = get_hooks_dir(git_root)
    config = load_config(git_root)

    hook_path = hooks_dir / args.hook
    if not hook_path.exists():
        print(f"❌ Hook '{args.hook}' no encontrado.")
        sys.exit(1)

    disabled_path = hooks_dir / f"{args.hook}.disabled"
    shutil.move(str(hook_path), str(disabled_path))

    if args.hook not in config.setdefault("disabled", []):
        config["disabled"].append(args.hook)

    save_config(git_root, config)
    print(f"⏸️  Hook deshabilitado: {args.hook}")


def cmd_enable(args):
    """Rehabilita un hook deshabilitado."""
    git_root = find_git_root(Path(args.path or "."))
    if not git_root:
        print("❌ No estás en un repositorio git.")
        sys.exit(1)

    hooks_dir = get_hooks_dir(git_root)
    config = load_config(git_root)

    disabled_path = hooks_dir / f"{args.hook}.disabled"
    hook_path = hooks_dir / args.hook

    if not disabled_path.exists():
        print(f"❌ Hook deshabilitado '{args.hook}' no encontrado.")
        sys.exit(1)

    shutil.move(str(disabled_path), str(hook_path))
    make_executable(hook_path)

    if args.hook in config.get("disabled", []):
        config["disabled"].remove(args.hook)

    save_config(git_root, config)
    print(f"▶️  Hook habilitado: {args.hook}")


def cmd_show(args):
    """Muestra el contenido de un hook."""
    if args.hook in HOOKS_LIBRARY:
        print(f"# Hook: {args.hook}")
        print(f"# {HOOKS_LIBRARY[args.hook]['description']}")
        print()
        print(HOOKS_LIBRARY[args.hook]["content"])
    else:
        print(f"❌ Hook '{args.hook}' no encontrado en la librería.")
        print(f"   Disponibles: {', '.join(HOOKS_LIBRARY.keys())}")
        sys.exit(1)


def cmd_add_custom(args):
    """Agrega un hook personalizado desde un archivo."""
    git_root = find_git_root(Path(args.path or "."))
    if not git_root:
        print("❌ No estás en un repositorio git.")
        sys.exit(1)

    hooks_dir = get_hooks_dir(git_root)
    source = Path(args.file)

    if not source.exists():
        print(f"❌ Archivo '{args.file}' no encontrado.")
        sys.exit(1)

    dest = hooks_dir / args.hook_name
    shutil.copy2(source, dest)
    make_executable(dest)

    print(f"✅ Hook custom instalado: {args.hook_name} → {dest}")


# ─── CLI ──────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        prog="ghm",
        description="Git Hooks Manager — Gestiona git hooks de forma automatizada",
    )
    parser.add_argument(
        "--path", "-p", default=".", help="Ruta al repositorio git (default: .)"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # list
    p_list = subparsers.add_parser("list", help="Lista hooks disponibles e instalados")
    p_list.set_defaults(func=cmd_list)

    # install
    p_install = subparsers.add_parser("install", help="Instala hooks en el repo")
    p_install.add_argument(
        "hooks",
        nargs="*",
        help="Nombre(s) del hook a instalar. Sin argumentos instala todos.",
    )
    p_install.add_argument("--all", "-a", action="store_true", help="Instala todos los hooks")
    p_install.add_argument(
        "--force", "-f", action="store_true", help="Sobreescribe hooks existentes sin backup"
    )
    p_install.set_defaults(func=cmd_install)

    # uninstall
    p_uninstall = subparsers.add_parser("uninstall", help="Desinstala hooks del repo")
    p_uninstall.add_argument("hooks", nargs="+", help="Nombre(s) del hook a desinstalar")
    p_uninstall.set_defaults(func=cmd_uninstall)

    # disable
    p_disable = subparsers.add_parser("disable", help="Deshabilita un hook temporalmente")
    p_disable.add_argument("hook", help="Nombre del hook a deshabilitar")
    p_disable.set_defaults(func=cmd_disable)

    # enable
    p_enable = subparsers.add_parser("enable", help="Rehabilita un hook deshabilitado")
    p_enable.add_argument("hook", help="Nombre del hook a habilitar")
    p_enable.set_defaults(func=cmd_enable)

    # show
    p_show = subparsers.add_parser("show", help="Muestra el contenido de un hook")
    p_show.add_argument("hook", help="Nombre del hook")
    p_show.set_defaults(func=cmd_show)

    # add-custom
    p_custom = subparsers.add_parser("add-custom", help="Agrega un hook personalizado desde archivo")
    p_custom.add_argument("hook_name", help="Nombre del hook (ej: pre-commit)")
    p_custom.add_argument("file", help="Ruta al archivo del hook")
    p_custom.set_defaults(func=cmd_add_custom)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
