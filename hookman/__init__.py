"""hookman — Git Hooks Manager.

Paquete modular para instalar, gestionar y sincronizar git hooks.
"""

from hookman.config import (
    VERSION,
    HOOKMAN_DIR,
    HOOKS_LIBRARY,
    PROFILES_FILE,
    VALID_HOOKS,
    BUILTIN_PROFILES,
)
from hookman.hooks.builtins import BUILTIN_HOOKS
from hookman.utils import (
    find_git_root,
    get_hooks_dir,
    hook_type,
    make_executable,
    is_executable,
)
from hookman.hooks.profiles import load_profiles, save_profiles
from hookman.commands import (
    cmd_list,
    cmd_install,
    cmd_uninstall,
    cmd_status,
    cmd_apply_profile,
    cmd_add_to_library,
    cmd_sync,
    cmd_disable,
    cmd_enable,
    cmd_init,
    cmd_export_profile,
)

__all__ = [
    "VERSION",
    "HOOKMAN_DIR",
    "HOOKS_LIBRARY",
    "PROFILES_FILE",
    "VALID_HOOKS",
    "BUILTIN_PROFILES",
    "BUILTIN_HOOKS",
    "find_git_root",
    "get_hooks_dir",
    "hook_type",
    "make_executable",
    "is_executable",
    "load_profiles",
    "save_profiles",
    "cmd_list",
    "cmd_install",
    "cmd_uninstall",
    "cmd_status",
    "cmd_apply_profile",
    "cmd_add_to_library",
    "cmd_sync",
    "cmd_disable",
    "cmd_enable",
    "cmd_init",
    "cmd_export_profile",
]
