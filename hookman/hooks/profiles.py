"""Gestión de perfiles de hooks (builtins + custom)."""

import json
from typing import Dict, List

from hookman.config import BUILTIN_PROFILES, PROFILES_FILE, ensure_hookman_dir


def load_profiles() -> dict:
    """Carga perfiles personalizados del archivo profiles.json."""
    ensure_hookman_dir()
    if PROFILES_FILE.exists():
        try:
            data = json.loads(PROFILES_FILE.read_text())
            if not isinstance(data, dict) or "profiles" not in data:
                return {"profiles": {}}
            return data
        except json.JSONDecodeError:
            return {"profiles": {}}
    return {"profiles": {}}


def save_profiles(data: dict) -> None:
    """Guarda perfiles personalizados al archivo profiles.json."""
    ensure_hookman_dir()
    if "profiles" not in data:
        data = {"profiles": data}
    PROFILES_FILE.write_text(json.dumps(data, indent=2, sort_keys=True))


def get_all_profiles() -> Dict[str, List[str]]:
    """Devuelve la combinación de perfiles builtin + usuario.

    Los perfiles del usuario sobrescriben a los builtins con el mismo nombre.
    """
    user = load_profiles().get("profiles", {})
    merged = dict(BUILTIN_PROFILES)
    merged.update(user)
    return merged


def create_profile(name: str, hooks: List[str]) -> None:
    """Crea o actualiza un perfil personalizado."""
    if not name or not isinstance(name, str):
        raise ValueError("El nombre del perfil debe ser un string no vacío")
    if not isinstance(hooks, (list, tuple)) or not hooks:
        raise ValueError("El perfil debe tener al menos un hook")
    data = load_profiles()
    data.setdefault("profiles", {})[name] = list(hooks)
    save_profiles(data)


def delete_profile(name: str) -> bool:
    """Elimina un perfil personalizado. Devuelve True si existía."""
    data = load_profiles()
    profiles = data.get("profiles", {})
    if name in profiles:
        del profiles[name]
        save_profiles(data)
        return True
    return False
