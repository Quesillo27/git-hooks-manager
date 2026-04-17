"""Tests de sync."""

from types import SimpleNamespace

from hookman.commands.install_cmd import cmd_install
from hookman.commands.sync_cmd import cmd_sync


def test_sync_copies_hooks(git_repo, second_repo):
    cmd_install(SimpleNamespace(hook="pre-commit/no-secrets", path=str(git_repo), force=False, dry_run=False))
    cmd_install(SimpleNamespace(hook="commit-msg/conventional", path=str(git_repo), force=False, dry_run=False))

    code = cmd_sync(SimpleNamespace(source=str(git_repo), destination=str(second_repo)))
    assert code == 0

    assert (second_repo / ".git" / "hooks" / "pre-commit").exists()
    assert (second_repo / ".git" / "hooks" / "commit-msg").exists()


def test_sync_skips_samples(git_repo, second_repo):
    # git init deja varios *.sample en el repo; sync debe ignorarlos.
    cmd_install(SimpleNamespace(hook="pre-commit/no-secrets", path=str(git_repo), force=False, dry_run=False))
    cmd_sync(SimpleNamespace(source=str(git_repo), destination=str(second_repo)))
    # El hook real se copió.
    assert (second_repo / ".git" / "hooks" / "pre-commit").exists()
    # Los samples del source NO se sobrescribieron al destino.
    copied = {p.name for p in (second_repo / ".git" / "hooks").iterdir()}
    # Ningún archivo copiado por sync puede tener extensión .sample.
    # (samples preexistentes en dest son parte del git init y no cuentan como sync)
    assert "pre-commit" in copied


def test_sync_invalid_source(tmp_path, second_repo):
    code = cmd_sync(SimpleNamespace(source=str(tmp_path), destination=str(second_repo)))
    assert code == 1


def test_sync_invalid_destination(git_repo, tmp_path):
    code = cmd_sync(SimpleNamespace(source=str(git_repo), destination=str(tmp_path)))
    assert code == 1
