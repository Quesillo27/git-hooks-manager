"""Comando `hookman install`."""

from pathlib import Path
from types import SimpleNamespace
from typing import Optional

from hookman.config import HOOKS_LIBRARY
from hookman.hooks.builtins import BUILTIN_HOOKS
from hookman.logger import get_logger
from hookman.utils import (
    find_git_root,
    get_hooks_dir,
    hook_type,
    make_executable,
)


HEADER_TEMPLATE = "#!/bin/bash\n# Instalado por hookman\n\n"


def _signature(content: str) -> str:
    """Extrae la firma `# hookman: <slug>` del contenido para detectar duplicados."""
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("# hookman:"):
            return stripped
    return ""


def _body_without_shebang(content: str) -> str:
    """Elimina la shebang (primera línea si es #!) y deja el cuerpo."""
    lines = content.strip().splitlines()
    if lines and lines[0].startswith("#!"):
        lines = lines[1:]
    return "\n".join(lines).strip() + "\n"


def _install_builtin(
    hook_name: str,
    hooks_dir: Path,
    force: bool,
    dry_run: bool,
) -> tuple:
    """Instala un hook builtin. Devuelve (installed, message)."""
    htype = hook_type(hook_name)
    target = hooks_dir / htype
    content = BUILTIN_HOOKS[hook_name]["content"]
    signature = _signature(content)

    if target.exists():
        existing = target.read_text()
        if signature and signature in existing and not force:
            return (False, f"Hook '{hook_name}' ya instalado en {htype}")
        if force:
            new_content = HEADER_TEMPLATE + _body_without_shebang(content)
        else:
            new_content = existing.rstrip() + "\n\n" + _body_without_shebang(content)
    else:
        new_content = HEADER_TEMPLATE + _body_without_shebang(content)

    if dry_run:
        return (True, f"[dry-run] instalaría '{hook_name}' en {target}")

    hooks_dir.mkdir(parents=True, exist_ok=True)
    target.write_text(new_content)
    make_executable(target)
    return (True, f"Hook '{hook_name}' instalado en .git/hooks/{htype}")


def _install_custom(
    hook_name: str,
    hooks_dir: Path,
    dry_run: bool,
) -> tuple:
    """Instala un hook desde la librería personalizada."""
    lib_file = HOOKS_LIBRARY / hook_name
    if not lib_file.exists() and not hook_name.endswith(".sh"):
        lib_file = HOOKS_LIBRARY / f"{hook_name}.sh"
    if not lib_file.exists():
        return (False, None)

    htype = hook_type(hook_name)
    target = hooks_dir / htype
    if dry_run:
        return (True, f"[dry-run] copiaría {lib_file} → {target}")

    hooks_dir.mkdir(parents=True, exist_ok=True)
    target.write_text(lib_file.read_text())
    make_executable(target)
    return (True, f"Hook personalizado '{hook_name}' instalado")


def install_one(
    hook_name: str,
    repo_path: Optional[Path] = None,
    force: bool = False,
    dry_run: bool = False,
) -> tuple:
    """Instala un hook en el repo dado.

    Returns:
        (success: bool, message: str)
    """
    logger = get_logger()
    git_root = find_git_root(repo_path)
    if not git_root:
        return (False, "No estás dentro de un repositorio git")

    hooks_dir = get_hooks_dir(git_root)

    if hook_name in BUILTIN_HOOKS:
        ok, msg = _install_builtin(hook_name, hooks_dir, force, dry_run)
        logger.info("install_builtin=%s hook=%s ok=%s", msg, hook_name, ok)
        return (ok, msg)

    ok, msg = _install_custom(hook_name, hooks_dir, dry_run)
    if ok:
        logger.info("install_custom=%s hook=%s", msg, hook_name)
        return (ok, msg)

    return (False, f"Hook '{hook_name}' no encontrado. Usa `hookman list`.")


def cmd_install(args: SimpleNamespace) -> int:
    """Entry point CLI del comando install."""
    repo_path = Path(getattr(args, "path", ".") or ".")
    force = bool(getattr(args, "force", False))
    dry_run = bool(getattr(args, "dry_run", False))
    ok, msg = install_one(args.hook, repo_path, force=force, dry_run=dry_run)
    print(("OK: " if ok else "ERROR: ") + msg)
    return 0 if ok else 1
