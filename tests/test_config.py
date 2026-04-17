"""Tests de config."""

from hookman.config import (
    BUILTIN_PROFILES,
    DEFAULT_LOG_LEVEL,
    HOOKMAN_DIR,
    HOOKS_LIBRARY,
    PROFILES_FILE,
    VALID_HOOKS,
    VERSION,
    ensure_hookman_dir,
)


def test_version_format():
    parts = VERSION.split(".")
    assert len(parts) == 3
    assert all(p.isdigit() for p in parts)


def test_valid_hooks_coverage():
    for expected in ("pre-commit", "commit-msg", "pre-push", "post-commit"):
        assert expected in VALID_HOOKS


def test_builtin_profiles_keys():
    for expected in ("basic", "python", "nodejs", "strict", "full"):
        assert expected in BUILTIN_PROFILES
        assert isinstance(BUILTIN_PROFILES[expected], list)
        assert len(BUILTIN_PROFILES[expected]) >= 1


def test_ensure_hookman_dir_creates_paths():
    # HOOKMAN_HOME ya está aislado por el fixture isolated_hookman_home
    ensure_hookman_dir()
    assert HOOKMAN_DIR.exists()
    assert HOOKS_LIBRARY.exists()
    assert PROFILES_FILE.exists()


def test_default_log_level_uppercase():
    assert DEFAULT_LOG_LEVEL == DEFAULT_LOG_LEVEL.upper()
