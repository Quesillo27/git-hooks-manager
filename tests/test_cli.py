"""Tests de la CLI (entry point principal)."""

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def _run(*args, cwd=None, env=None):
    cmd = [sys.executable, "-m", "hookman", *args]
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=cwd or str(ROOT),
        env=env,
        timeout=30,
    )


@pytest.fixture
def cli_env(tmp_path, monkeypatch):
    import os

    env = os.environ.copy()
    env["HOOKMAN_HOME"] = str(tmp_path / "hm")
    return env


def test_cli_version(cli_env):
    r = _run("--version", env=cli_env)
    assert r.returncode == 0
    assert "hookman" in r.stdout.lower() or "hookman" in r.stderr.lower()


def test_cli_help(cli_env):
    r = _run("--help", env=cli_env)
    assert r.returncode == 0
    assert "hookman" in r.stdout.lower()
    assert "install" in r.stdout
    assert "profile" in r.stdout


def test_cli_list(cli_env):
    r = _run("list", env=cli_env)
    assert r.returncode == 0
    assert "pre-commit" in r.stdout
    assert "conventional" in r.stdout


def test_cli_list_json(cli_env):
    r = _run("list", "--json", env=cli_env)
    assert r.returncode == 0
    import json

    data = json.loads(r.stdout)
    assert "builtin" in data


def test_cli_status_outside_repo(cli_env, tmp_path):
    r = _run("status", str(tmp_path), env=cli_env)
    assert r.returncode == 1


def test_cli_install_and_status(cli_env, tmp_path):
    import subprocess as sp

    repo = tmp_path / "r"
    repo.mkdir()
    sp.run(["git", "init", str(repo)], capture_output=True, check=True)

    r = _run(
        "install",
        "pre-commit/no-secrets",
        "--path",
        str(repo),
        env=cli_env,
    )
    assert r.returncode == 0, r.stderr

    r2 = _run("status", str(repo), env=cli_env)
    assert r2.returncode == 0
    assert "pre-commit" in r2.stdout


def test_cli_profile_dry_run(cli_env, tmp_path):
    import subprocess as sp

    repo = tmp_path / "r"
    repo.mkdir()
    sp.run(["git", "init", str(repo)], capture_output=True, check=True)

    r = _run(
        "profile",
        "basic",
        "--path",
        str(repo),
        "--dry-run",
        env=cli_env,
    )
    assert r.returncode == 0
    assert "dry-run" in r.stdout
    assert not (repo / ".git" / "hooks" / "pre-commit").exists()


def test_cli_legacy_script_invokes(cli_env):
    """El archivo hookman.py del root sigue siendo ejecutable."""
    r = subprocess.run(
        [sys.executable, str(ROOT / "hookman.py"), "--version"],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
        env=cli_env,
        timeout=30,
    )
    assert r.returncode == 0


def test_cli_legacy_git_hooks_manager(cli_env, tmp_path):
    """El archivo legacy git_hooks_manager.py aún funciona."""
    import subprocess as sp

    repo = tmp_path / "r"
    repo.mkdir()
    sp.run(["git", "init", str(repo)], capture_output=True, check=True)

    r = subprocess.run(
        [
            sys.executable,
            str(ROOT / "git_hooks_manager.py"),
            "--path",
            str(repo),
            "list",
        ],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
        env=cli_env,
        timeout=30,
    )
    assert r.returncode == 0
    assert "pre-commit" in r.stdout
