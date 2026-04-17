"""Comando `hookman export-profile` — exporta un perfil a JSON."""

import json
from pathlib import Path
from types import SimpleNamespace

from hookman.hooks.profiles import get_all_profiles


def cmd_export_profile(args: SimpleNamespace) -> int:
    """Exporta un perfil a JSON (stdout u archivo)."""
    profiles = get_all_profiles()
    name = args.profile
    if name not in profiles:
        print(f"ERROR: perfil '{name}' no encontrado")
        print(f"  Disponibles: {', '.join(sorted(profiles.keys()))}")
        return 1

    payload = {"profile": name, "hooks": profiles[name]}
    dest = getattr(args, "output", None)

    text = json.dumps(payload, indent=2, sort_keys=True)
    if dest:
        Path(dest).write_text(text + "\n")
        print(f"OK: perfil '{name}' exportado a {dest}")
    else:
        print(text)
    return 0
