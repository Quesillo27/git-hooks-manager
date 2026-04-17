"""Tests del shim legacy git_hooks_manager.py y hookman.py."""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_git_hooks_manager_imports_and_exposes_api():
    import git_hooks_manager

    assert hasattr(git_hooks_manager, "HOOKS")
    assert "pre-commit" in git_hooks_manager.HOOKS
    assert hasattr(git_hooks_manager, "install_hook")
    assert hasattr(git_hooks_manager, "remove_hook")
    assert hasattr(git_hooks_manager, "list_hooks")
    assert hasattr(git_hooks_manager, "find_git_root")


def test_legacy_install_and_remove(git_repo):
    import git_hooks_manager as ghm

    ok = ghm.install_hook(git_repo, "pre-commit")
    assert ok is True
    hook = git_repo / ".git" / "hooks" / "pre-commit"
    assert hook.exists()

    ok = ghm.remove_hook(git_repo, "pre-commit")
    assert ok is True
    assert not hook.exists()


def test_legacy_unknown_hook_returns_false(git_repo):
    import git_hooks_manager as ghm

    ok = ghm.install_hook(git_repo, "not-a-hook")
    assert ok is False


def test_hookman_module_reexports_package():
    import hookman

    assert hasattr(hookman, "VERSION")
    assert hasattr(hookman, "BUILTIN_HOOKS")
    assert hasattr(hookman, "cmd_install")
    assert len(hookman.BUILTIN_HOOKS) >= 7


def test_legacy_script_list_command(git_repo):
    env = os.environ.copy()
    env["HOOKMAN_HOME"] = str(git_repo / "hm")
    r = subprocess.run(
        [
            sys.executable,
            str(ROOT / "git_hooks_manager.py"),
            "--path",
            str(git_repo),
            "list",
        ],
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
    )
    assert r.returncode == 0
    assert "pre-commit" in r.stdout
