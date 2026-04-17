"""Tests de disable/enable."""

from types import SimpleNamespace

from hookman.commands.disable_cmd import cmd_disable, cmd_enable
from hookman.commands.install_cmd import cmd_install
from hookman.utils import is_executable


def _install(repo, name="pre-commit/no-secrets"):
    cmd_install(SimpleNamespace(hook=name, path=str(repo), force=False, dry_run=False))


def test_disable_renames_hook(git_repo):
    _install(git_repo)
    hook = git_repo / ".git" / "hooks" / "pre-commit"
    assert hook.exists()

    code = cmd_disable(SimpleNamespace(hook="pre-commit", path=str(git_repo)))
    assert code == 0
    assert not hook.exists()
    assert (git_repo / ".git" / "hooks" / "pre-commit.disabled").exists()


def test_enable_restores_hook(git_repo):
    _install(git_repo)
    cmd_disable(SimpleNamespace(hook="pre-commit", path=str(git_repo)))
    code = cmd_enable(SimpleNamespace(hook="pre-commit", path=str(git_repo)))
    assert code == 0

    hook = git_repo / ".git" / "hooks" / "pre-commit"
    assert hook.exists()
    assert is_executable(hook)
    assert not (git_repo / ".git" / "hooks" / "pre-commit.disabled").exists()


def test_disable_missing_hook_errors(git_repo):
    code = cmd_disable(SimpleNamespace(hook="pre-push", path=str(git_repo)))
    assert code == 1


def test_enable_without_disabled_errors(git_repo):
    code = cmd_enable(SimpleNamespace(hook="pre-commit", path=str(git_repo)))
    assert code == 1


def test_disable_outside_repo(tmp_path):
    code = cmd_disable(SimpleNamespace(hook="pre-commit", path=str(tmp_path)))
    assert code == 1
