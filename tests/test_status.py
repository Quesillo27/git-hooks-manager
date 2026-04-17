"""Tests de status."""

import json
from io import StringIO
from types import SimpleNamespace

from hookman.commands.install_cmd import cmd_install
from hookman.commands.status_cmd import cmd_status


def test_status_empty_repo(git_repo, capsys):
    cmd_status(SimpleNamespace(path=str(git_repo), json=False))
    captured = capsys.readouterr().out
    assert "ningún hook" in captured or "ninguno" in captured.lower() or "ningun" in captured.lower()


def test_status_lists_installed_hooks(git_repo, capsys):
    cmd_install(SimpleNamespace(hook="pre-commit/no-secrets", path=str(git_repo), force=False, dry_run=False))
    cmd_status(SimpleNamespace(path=str(git_repo), json=False))
    out = capsys.readouterr().out
    assert "pre-commit" in out
    assert "installed" in out


def test_status_json_output(git_repo, capsys):
    cmd_install(SimpleNamespace(hook="pre-commit/no-secrets", path=str(git_repo), force=False, dry_run=False))
    capsys.readouterr()  # descartar output del install
    cmd_status(SimpleNamespace(path=str(git_repo), json=True))
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "hooks" in data
    assert any(h["name"] == "pre-commit" for h in data["hooks"])
    installed = [h for h in data["hooks"] if h["state"] == "installed"][0]
    assert installed["executable"] is True


def test_status_outside_repo_errors(tmp_path, capsys):
    code = cmd_status(SimpleNamespace(path=str(tmp_path), json=False))
    assert code == 1
