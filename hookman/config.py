"""Configuración centralizada de hookman.

Las rutas pueden sobreescribirse vía variables de entorno:
- HOOKMAN_HOME: directorio raíz (default: ~/.hookman)
"""

import os
from pathlib import Path

VERSION = "2.0.0"

HOOKMAN_DIR = Path(os.environ.get("HOOKMAN_HOME", str(Path.home() / ".hookman")))
HOOKS_LIBRARY = HOOKMAN_DIR / "library"
PROFILES_FILE = HOOKMAN_DIR / "profiles.json"
LOG_FILE = HOOKMAN_DIR / "hookman.log"

VALID_HOOKS = (
    "pre-commit",
    "prepare-commit-msg",
    "commit-msg",
    "post-commit",
    "pre-push",
    "pre-rebase",
    "post-checkout",
    "post-merge",
    "pre-receive",
    "update",
    "post-receive",
    "applypatch-msg",
    "pre-applypatch",
    "post-applypatch",
    "fsmonitor-watchman",
    "post-rewrite",
    "post-update",
    "push-to-checkout",
)

BUILTIN_PROFILES = {
    "python": [
        "pre-commit/no-secrets",
        "pre-commit/lint-python",
        "commit-msg/conventional",
        "pre-push/run-tests",
    ],
    "nodejs": [
        "pre-commit/no-secrets",
        "pre-commit/lint-js",
        "commit-msg/conventional",
        "pre-push/run-tests",
    ],
    "basic": [
        "pre-commit/no-secrets",
        "commit-msg/conventional",
    ],
    "strict": [
        "pre-commit/no-secrets",
        "pre-commit/no-large-files",
        "commit-msg/conventional",
        "pre-push/run-tests",
    ],
    "full": [
        "pre-commit/no-secrets",
        "pre-commit/no-large-files",
        "pre-commit/lint-python",
        "pre-commit/lint-js",
        "commit-msg/conventional",
        "pre-push/run-tests",
        "post-commit/notify",
    ],
}

DEFAULT_LOG_LEVEL = os.environ.get("HOOKMAN_LOG_LEVEL", "INFO").upper()
DEFAULT_LARGE_FILE_BYTES = int(os.environ.get("HOOKMAN_MAX_FILE_BYTES", str(1024 * 1024)))


def ensure_hookman_dir() -> None:
    """Crea el directorio de hookman si no existe e inicializa profiles.json."""
    import json

    HOOKMAN_DIR.mkdir(parents=True, exist_ok=True)
    HOOKS_LIBRARY.mkdir(parents=True, exist_ok=True)
    if not PROFILES_FILE.exists():
        PROFILES_FILE.write_text(json.dumps({"profiles": {}}, indent=2))
