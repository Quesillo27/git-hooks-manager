"""Submódulo con definiciones de hooks (builtins, perfiles, librería)."""

from hookman.hooks.builtins import BUILTIN_HOOKS
from hookman.hooks.profiles import (
    load_profiles,
    save_profiles,
    get_all_profiles,
    create_profile,
    delete_profile,
)

__all__ = [
    "BUILTIN_HOOKS",
    "load_profiles",
    "save_profiles",
    "get_all_profiles",
    "create_profile",
    "delete_profile",
]
