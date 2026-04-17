"""Shim de compatibilidad — re-exporta la API del paquete `hookman`.

Se mantiene por compatibilidad con el uso histórico:
    python hookman.py <comando>

El código real vive en el paquete `hookman/`.
"""

import sys
from pathlib import Path

# Permitir que `import hookman` resuelva el paquete incluso cuando este
# archivo está en el mismo directorio.
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from hookman import (  # noqa: E402
    BUILTIN_HOOKS,
    BUILTIN_PROFILES,
    HOOKMAN_DIR,
    HOOKS_LIBRARY,
    PROFILES_FILE,
    VALID_HOOKS,
    VERSION,
    cmd_add_to_library,
    cmd_apply_profile,
    cmd_disable,
    cmd_enable,
    cmd_export_profile,
    cmd_init,
    cmd_install,
    cmd_list,
    cmd_status,
    cmd_sync,
    cmd_uninstall,
    find_git_root,
    get_hooks_dir,
    hook_type,
    is_executable,
    load_profiles,
    make_executable,
    save_profiles,
)
from hookman.cli import main  # noqa: E402
from hookman.config import ensure_hookman_dir  # noqa: E402


def _legacy_main() -> int:
    """Preserva el entry point directo del archivo."""
    return main()


if __name__ == "__main__":
    sys.exit(_legacy_main())
