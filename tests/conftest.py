"""Fixtures comunes de pytest para hookman."""

import os
import subprocess
import sys
from pathlib import Path

import pytest

# Asegurar que el paquete hookman del repo sea importable
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(autouse=True)
def isolated_hookman_home(tmp_path, monkeypatch):
    """Aísla HOOKMAN_HOME por test para no tocar ~/.hookman del usuario."""
    home = tmp_path / "hookman_home"
    home.mkdir()
    monkeypatch.setenv("HOOKMAN_HOME", str(home))

    # Reimportar módulos que leen env en import-time
    for mod_name in [
        "hookman",
        "hookman.config",
        "hookman.logger",
        "hookman.utils",
        "hookman.hooks",
        "hookman.hooks.builtins",
        "hookman.hooks.profiles",
        "hookman.commands",
        "hookman.commands.list_cmd",
        "hookman.commands.install_cmd",
        "hookman.commands.uninstall_cmd",
        "hookman.commands.status_cmd",
        "hookman.commands.profile_cmd",
        "hookman.commands.add_cmd",
        "hookman.commands.sync_cmd",
        "hookman.commands.disable_cmd",
        "hookman.commands.init_cmd",
        "hookman.commands.export_cmd",
        "hookman.cli",
    ]:
        sys.modules.pop(mod_name, None)

    yield home


@pytest.fixture
def git_repo(tmp_path):
    """Crea un repo git vacío y devuelve su Path."""
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(
        ["git", "init", str(repo)],
        capture_output=True,
        check=True,
    )
    return repo


@pytest.fixture
def second_repo(tmp_path):
    """Crea un segundo repo para tests de sync."""
    repo = tmp_path / "repo2"
    repo.mkdir()
    subprocess.run(
        ["git", "init", str(repo)],
        capture_output=True,
        check=True,
    )
    return repo
