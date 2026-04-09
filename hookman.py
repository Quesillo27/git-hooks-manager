#!/usr/bin/env python3
"""
hookman — Git Hooks Manager
Instala, gestiona y sincroniza git hooks entre proyectos.
"""

import argparse
import os
import stat
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

# ── Constantes ──────────────────────────────────────────────────────────────

VERSION = "1.0.0"
HOOKMAN_DIR = Path.home() / ".hookman"
HOOKS_LIBRARY = HOOKMAN_DIR / "library"
PROFILES_FILE = HOOKMAN_DIR / "profiles.json"
VALID_HOOKS = [
    "pre-commit", "prepare-commit-msg", "commit-msg", "post-commit",
    "pre-push", "pre-rebase", "post-checkout", "post-merge",
    "pre-receive", "update", "post-receive",
]

# ── Templates de hooks incluidos ─────────────────────────────────────────────

BUILTIN_HOOKS = {
    "pre-commit/no-secrets": {
        "description": "Previene commitear archivos con posibles secretos",
        "content": r"""#!/bin/bash
# hookman: no-secrets — Detecta posibles credenciales antes del commit
PATTERNS="password\s*=\s*['\"][^'\"\$]\|secret\s*=\s*['\"][^'\"\$]\|api_key\s*=\s*['\"][^'\"\$]\|BEGIN RSA PRIVATE KEY\|BEGIN EC PRIVATE KEY"
FILES=$(git diff --cached --name-only --diff-filter=ACM)
FOUND=0
for FILE in $FILES; do
    if echo "$FILE" | grep -qiE "\.(env|pem|key|pfx|p12)$"; then
        echo "⛔ Posible archivo de secretos: $FILE"
        FOUND=1
    fi
    if git show ":$FILE" 2>/dev/null | grep -qiE "$PATTERNS"; then
        echo "⛔ Posible secreto en: $FILE"
        FOUND=1
    fi
done
if [ "$FOUND" -eq 1 ]; then
    echo "❌ Commit bloqueado. Revisa los archivos indicados."
    exit 1
fi
exit 0
"""
    },
    "pre-commit/lint-python": {
        "description": "Ejecuta flake8 en archivos Python modificados",
        "content": r"""#!/bin/bash
# hookman: lint-python — Lintea archivos Python antes del commit
PY_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep "\.py$")
if [ -z "$PY_FILES" ]; then exit 0; fi
if ! command -v flake8 &>/dev/null; then
    echo "⚠️  flake8 no instalado — saltando lint Python"
    exit 0
fi
echo "🔍 Lintando Python..."
echo "$PY_FILES" | xargs flake8 --max-line-length=100
if [ $? -ne 0 ]; then
    echo "❌ Errores de lint encontrados. Corrige antes de commitear."
    exit 1
fi
exit 0
"""
    },
    "pre-commit/lint-js": {
        "description": "Ejecuta eslint en archivos JS/TS modificados",
        "content": r"""#!/bin/bash
# hookman: lint-js — Lintea archivos JS/TS antes del commit
JS_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep -E "\.(js|jsx|ts|tsx)$")
if [ -z "$JS_FILES" ]; then exit 0; fi
if ! command -v npx &>/dev/null; then exit 0; fi
if [ ! -f ".eslintrc*" ] && [ ! -f "eslint.config*" ] && ! grep -q '"eslintConfig"' package.json 2>/dev/null; then
    echo "⚠️  ESLint no configurado — saltando lint JS"
    exit 0
fi
echo "🔍 Lintando JS/TS..."
echo "$JS_FILES" | xargs npx eslint --no-error-on-unmatched-pattern
if [ $? -ne 0 ]; then
    echo "❌ Errores de ESLint. Corrige antes de commitear."
    exit 1
fi
exit 0
"""
    },
    "pre-commit/no-large-files": {
        "description": "Previene commitear archivos mayores a 1MB",
        "content": r"""#!/bin/bash
# hookman: no-large-files — Bloquea archivos grandes (>1MB)
MAX_SIZE=1048576  # 1MB en bytes
FILES=$(git diff --cached --name-only --diff-filter=ACM)
FOUND=0
for FILE in $FILES; do
    if [ -f "$FILE" ]; then
        SIZE=$(wc -c < "$FILE")
        if [ "$SIZE" -gt "$MAX_SIZE" ]; then
            echo "⛔ Archivo demasiado grande: $FILE ($(( SIZE / 1024 ))KB)"
            FOUND=1
        fi
    fi
done
if [ "$FOUND" -eq 1 ]; then
    echo "❌ Commit bloqueado. Usa Git LFS para archivos grandes."
    exit 1
fi
exit 0
"""
    },
    "commit-msg/conventional": {
        "description": "Valida formato de Conventional Commits",
        "content": r"""#!/bin/bash
# hookman: conventional-commits — Valida formato de commit message
COMMIT_MSG=$(cat "$1")
PATTERN="^(feat|fix|docs|style|refactor|perf|test|chore|ci|build|revert)(\(.+\))?: .{3,}"
if ! echo "$COMMIT_MSG" | grep -qE "$PATTERN"; then
    echo "❌ Commit message inválido."
    echo "   Formato esperado: <tipo>(scope?): descripción"
    echo "   Tipos válidos: feat|fix|docs|style|refactor|perf|test|chore|ci|build|revert"
    echo "   Ejemplo: feat(auth): add JWT refresh token"
    exit 1
fi
exit 0
"""
    },
    "pre-push/run-tests": {
        "description": "Ejecuta npm test o pytest antes de push",
        "content": r"""#!/bin/bash
# hookman: run-tests — Ejecuta tests antes del push
if [ -f "package.json" ] && grep -q '"test"' package.json; then
    echo "🧪 Ejecutando npm test..."
    npm test
    if [ $? -ne 0 ]; then
        echo "❌ Tests fallaron. Corrige antes de hacer push."
        exit 1
    fi
elif [ -f "requirements.txt" ] && command -v pytest &>/dev/null; then
    echo "🧪 Ejecutando pytest..."
    pytest --tb=short -q
    if [ $? -ne 0 ]; then
        echo "❌ Tests fallaron. Corrige antes de hacer push."
        exit 1
    fi
fi
exit 0
"""
    },
    "post-commit/notify": {
        "description": "Muestra resumen del commit al terminar",
        "content": r"""#!/bin/bash
# hookman: notify — Muestra resumen del commit
COMMIT=$(git log -1 --format="%h %s" HEAD)
BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "✅ Commit en [$BRANCH]: $COMMIT"
"""
    },
}

# ── Helpers ──────────────────────────────────────────────────────────────────

def ensure_hookman_dir():
    HOOKMAN_DIR.mkdir(parents=True, exist_ok=True)
    HOOKS_LIBRARY.mkdir(parents=True, exist_ok=True)
    if not PROFILES_FILE.exists():
        PROFILES_FILE.write_text(json.dumps({"profiles": {}}, indent=2))


def load_profiles() -> dict:
    if PROFILES_FILE.exists():
        return json.loads(PROFILES_FILE.read_text())
    return {"profiles": {}}


def save_profiles(data: dict):
    PROFILES_FILE.write_text(json.dumps(data, indent=2))


def find_git_root(path: Path = None) -> Path:
    """Sube en el árbol hasta encontrar .git"""
    p = path or Path.cwd()
    while p != p.parent:
        if (p / ".git").is_dir():
            return p
        p = p.parent
    return None


def get_hooks_dir(repo_path: Path) -> Path:
    return repo_path / ".git" / "hooks"


def make_executable(path: Path):
    path.chmod(path.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)


def hook_type(name: str) -> str:
    """Extrae el tipo de hook del nombre (pre-commit/lint → pre-commit)"""
    return name.split("/")[0]


# ── Comandos ─────────────────────────────────────────────────────────────────

def cmd_list(args):
    """Lista hooks disponibles en la librería"""
    print(f"\n{'─'*60}")
    print(f"  Hooks integrados ({len(BUILTIN_HOOKS)} disponibles)")
    print(f"{'─'*60}")

    by_type = {}
    for name, info in BUILTIN_HOOKS.items():
        htype = hook_type(name)
        by_type.setdefault(htype, []).append((name, info))

    for htype, hooks in sorted(by_type.items()):
        print(f"\n  [{htype}]")
        for name, info in hooks:
            short_name = name.split("/")[1]
            print(f"    • {short_name:<25} {info['description']}")

    # Hooks personalizados en librería
    custom = list(HOOKS_LIBRARY.rglob("*.sh"))
    if custom:
        print(f"\n  Hooks personalizados ({len(custom)}):")
        for f in custom:
            rel = f.relative_to(HOOKS_LIBRARY)
            print(f"    • {rel}")

    print()


def cmd_install(args):
    """Instala un hook en el repo actual"""
    git_root = find_git_root()
    if not git_root:
        print("❌ No estás dentro de un repositorio git")
        sys.exit(1)

    hooks_dir = get_hooks_dir(git_root)
    hook_name = args.hook  # ej: "pre-commit/no-secrets" o "pre-commit"

    # Buscar en builtins
    if hook_name in BUILTIN_HOOKS:
        htype = hook_type(hook_name)
        hook_file = hooks_dir / htype
        content = BUILTIN_HOOKS[hook_name]["content"]

        # Si ya existe el hook, hacer append
        if hook_file.exists():
            existing = hook_file.read_text()
            if BUILTIN_HOOKS[hook_name]["content"].split("\n")[1] in existing:
                print(f"⚠️  Hook '{hook_name}' ya instalado en {git_root.name}")
                return
            # Append al hook existente
            hook_file.write_text(existing.rstrip() + "\n\n" + "\n".join(content.strip().split("\n")[1:]) + "\n")
        else:
            hook_file.write_text("#!/bin/bash\n# Instalado por hookman\n\n" + "\n".join(content.strip().split("\n")[1:]) + "\n")

        make_executable(hook_file)
        print(f"✅ Hook '{hook_name}' instalado en {git_root.name}/.git/hooks/{htype}")
        return

    # Buscar en librería personalizada
    lib_file = HOOKS_LIBRARY / hook_name
    if not lib_file.exists() and not hook_name.endswith(".sh"):
        lib_file = HOOKS_LIBRARY / f"{hook_name}.sh"

    if lib_file.exists():
        htype = hook_type(hook_name)
        hook_file = hooks_dir / htype
        content = lib_file.read_text()
        hook_file.write_text(content)
        make_executable(hook_file)
        print(f"✅ Hook personalizado '{hook_name}' instalado")
        return

    print(f"❌ Hook '{hook_name}' no encontrado")
    print(f"   Usa 'hookman list' para ver hooks disponibles")
    sys.exit(1)


def cmd_uninstall(args):
    """Elimina un hook del repo actual"""
    git_root = find_git_root()
    if not git_root:
        print("❌ No estás dentro de un repositorio git")
        sys.exit(1)

    hooks_dir = get_hooks_dir(git_root)
    htype = hook_type(args.hook)
    hook_file = hooks_dir / htype

    if not hook_file.exists():
        print(f"⚠️  Hook '{htype}' no estaba instalado")
        return

    hook_file.unlink()
    print(f"✅ Hook '{htype}' eliminado de {git_root.name}")


def cmd_status(args):
    """Muestra hooks instalados en el repo actual"""
    path = Path(args.path) if args.path else None
    git_root = find_git_root(path)

    if not git_root:
        print("❌ No se encontró repositorio git")
        sys.exit(1)

    hooks_dir = get_hooks_dir(git_root)
    print(f"\n  Hooks en: {git_root}")
    print(f"{'─'*50}")

    found = False
    for h in sorted(VALID_HOOKS):
        hook_file = hooks_dir / h
        if hook_file.exists():
            size = hook_file.stat().st_size
            is_exec = os.access(hook_file, os.X_OK)
            status = "✅" if is_exec else "⚠️ (sin permisos)"
            print(f"  {status} {h:<30} ({size} bytes)")
            found = True

    if not found:
        print("  (ningún hook instalado)")

    print()


def cmd_apply_profile(args):
    """Aplica un perfil predefinido de hooks"""
    profiles_data = load_profiles()
    profiles = profiles_data.get("profiles", {})

    # Perfiles integrados
    builtin_profiles = {
        "python": ["pre-commit/no-secrets", "pre-commit/lint-python", "commit-msg/conventional", "pre-push/run-tests"],
        "nodejs": ["pre-commit/no-secrets", "pre-commit/lint-js", "commit-msg/conventional", "pre-push/run-tests"],
        "basic":  ["pre-commit/no-secrets", "commit-msg/conventional"],
        "strict": ["pre-commit/no-secrets", "pre-commit/no-large-files", "commit-msg/conventional", "pre-push/run-tests"],
    }
    all_profiles = {**builtin_profiles, **profiles}

    profile_name = args.profile
    if profile_name not in all_profiles:
        print(f"❌ Perfil '{profile_name}' no encontrado")
        print(f"   Perfiles disponibles: {', '.join(all_profiles.keys())}")
        sys.exit(1)

    hooks_to_install = all_profiles[profile_name]
    print(f"📦 Aplicando perfil '{profile_name}' ({len(hooks_to_install)} hooks)...")

    for hook in hooks_to_install:
        class FakeArgs:
            pass
        fa = FakeArgs()
        fa.hook = hook
        cmd_install(fa)


def cmd_add_to_library(args):
    """Agrega un script personalizado a la librería"""
    src = Path(args.file)
    if not src.exists():
        print(f"❌ Archivo '{args.file}' no encontrado")
        sys.exit(1)

    # Determinar tipo
    htype = args.type or "pre-commit"
    if htype not in VALID_HOOKS:
        print(f"❌ Tipo de hook inválido: {htype}")
        print(f"   Tipos válidos: {', '.join(VALID_HOOKS)}")
        sys.exit(1)

    dest_name = args.name or src.stem
    dest_dir = HOOKS_LIBRARY / htype
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"{dest_name}.sh"

    shutil.copy2(src, dest)
    make_executable(dest)
    print(f"✅ Hook '{htype}/{dest_name}' agregado a la librería")


def cmd_sync(args):
    """Sincroniza hooks de un repo a otro"""
    src_root = find_git_root(Path(args.source))
    dst_root = find_git_root(Path(args.destination))

    if not src_root:
        print(f"❌ Fuente no es un repo git: {args.source}")
        sys.exit(1)
    if not dst_root:
        print(f"❌ Destino no es un repo git: {args.destination}")
        sys.exit(1)

    src_hooks = get_hooks_dir(src_root)
    dst_hooks = get_hooks_dir(dst_root)

    copied = 0
    for h in VALID_HOOKS:
        src_file = src_hooks / h
        if src_file.exists() and not src_file.name.endswith(".sample"):
            dst_file = dst_hooks / h
            shutil.copy2(src_file, dst_file)
            make_executable(dst_file)
            copied += 1

    print(f"✅ {copied} hook(s) sincronizados de {src_root.name} → {dst_root.name}")


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    ensure_hookman_dir()

    parser = argparse.ArgumentParser(
        prog="hookman",
        description="🪝 Git Hooks Manager — instala y gestiona git hooks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  hookman list                          # ver hooks disponibles
  hookman install pre-commit/no-secrets # instalar hook
  hookman install commit-msg/conventional
  hookman profile nodejs                # aplicar perfil Node.js
  hookman status                        # ver hooks instalados
  hookman sync ./proyecto-a ./proyecto-b
        """
    )
    parser.add_argument("--version", action="version", version=f"hookman {VERSION}")

    sub = parser.add_subparsers(dest="command", metavar="<comando>")

    # list
    p_list = sub.add_parser("list", help="Lista hooks disponibles en la librería")
    p_list.set_defaults(func=cmd_list)

    # install
    p_install = sub.add_parser("install", help="Instala un hook en el repo actual")
    p_install.add_argument("hook", help="Nombre del hook (ej: pre-commit/no-secrets)")
    p_install.set_defaults(func=cmd_install)

    # uninstall
    p_uninstall = sub.add_parser("uninstall", help="Elimina un hook del repo actual")
    p_uninstall.add_argument("hook", help="Nombre del hook (ej: pre-commit)")
    p_uninstall.set_defaults(func=cmd_uninstall)

    # status
    p_status = sub.add_parser("status", help="Muestra hooks instalados en el repo")
    p_status.add_argument("path", nargs="?", help="Ruta al repo (default: cwd)")
    p_status.set_defaults(func=cmd_status)

    # profile
    p_profile = sub.add_parser("profile", help="Aplica un perfil de hooks (python|nodejs|basic|strict)")
    p_profile.add_argument("profile", help="Nombre del perfil")
    p_profile.set_defaults(func=cmd_apply_profile)

    # add
    p_add = sub.add_parser("add", help="Agrega un script personalizado a la librería")
    p_add.add_argument("file", help="Ruta al script .sh")
    p_add.add_argument("--type", help=f"Tipo de hook (default: pre-commit)")
    p_add.add_argument("--name", help="Nombre en la librería (default: nombre del archivo)")
    p_add.set_defaults(func=cmd_add_to_library)

    # sync
    p_sync = sub.add_parser("sync", help="Sincroniza hooks entre dos repos")
    p_sync.add_argument("source", help="Repo fuente")
    p_sync.add_argument("destination", help="Repo destino")
    p_sync.set_defaults(func=cmd_sync)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
