"""Comando `hookman profile` — aplica un perfil completo de hooks."""

from pathlib import Path
from types import SimpleNamespace

from hookman.commands.install_cmd import install_one
from hookman.hooks.profiles import get_all_profiles


def cmd_apply_profile(args: SimpleNamespace) -> int:
    """Aplica un perfil builtin o personalizado."""
    profiles = get_all_profiles()
    name = args.profile
    if name not in profiles:
        print(f"ERROR: perfil '{name}' no encontrado")
        print(f"  Disponibles: {', '.join(sorted(profiles.keys()))}")
        return 1

    repo_path = Path(getattr(args, "path", ".") or ".")
    force = bool(getattr(args, "force", False))
    dry_run = bool(getattr(args, "dry_run", False))

    hooks = profiles[name]
    print(f"OK: aplicando perfil '{name}' ({len(hooks)} hooks)")
    failed = 0
    for hook in hooks:
        ok, msg = install_one(hook, repo_path, force=force, dry_run=dry_run)
        print(("  OK: " if ok else "  ERROR: ") + msg)
        if not ok:
            failed += 1
    return 0 if failed == 0 else 1
