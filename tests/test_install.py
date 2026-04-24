"""Tests de instalación/desinstalación."""

from types import SimpleNamespace

from hookman.commands.install_cmd import cmd_install, install_one
from hookman.commands.uninstall_cmd import cmd_uninstall
from hookman.utils import is_executable


def _args(hook, path, **extra):
    ns = SimpleNamespace(hook=hook, path=str(path), force=False, dry_run=False)
    for k, v in extra.items():
        setattr(ns, k, v)
    return ns


def test_install_creates_executable_hook(git_repo):
    code = cmd_install(_args("pre-commit/no-secrets", git_repo))
    assert code == 0
    hook_file = git_repo / ".git" / "hooks" / "pre-commit"
    assert hook_file.exists()
    assert is_executable(hook_file)
    assert "hookman: no-secrets" in hook_file.read_text()


def test_install_unknown_hook_fails(git_repo):
    code = cmd_install(_args("pre-commit/does-not-exist", git_repo))
    assert code == 1


def test_install_outside_repo_fails(tmp_path):
    code = cmd_install(_args("pre-commit/no-secrets", tmp_path))
    assert code == 1


def test_install_duplicate_detected(git_repo):
    cmd_install(_args("pre-commit/no-secrets", git_repo))
    ok, msg = install_one("pre-commit/no-secrets", git_repo)
    assert ok is False
    assert "ya instalado" in msg


def test_install_force_overwrites(git_repo):
    cmd_install(_args("pre-commit/no-secrets", git_repo))
    hook_file = git_repo / ".git" / "hooks" / "pre-commit"
    original = hook_file.read_text()
    cmd_install(_args("pre-commit/no-secrets", git_repo, force=True))
    new_content = hook_file.read_text()
    assert "hookman: no-secrets" in new_content
    # Con --force el archivo se recrea (mismo contenido), no se duplica.
    assert new_content.count("# hookman: no-secrets") == 1


def test_install_chains_different_hooks_same_type(git_repo):
    cmd_install(_args("pre-commit/no-secrets", git_repo))
    cmd_install(_args("pre-commit/no-large-files", git_repo))
    hook_file = git_repo / ".git" / "hooks" / "pre-commit"
    content = hook_file.read_text()
    assert "hookman: no-secrets" in content
    assert "hookman: no-large-files" in content


def test_install_dry_run_does_not_write(git_repo):
    code = cmd_install(_args("pre-commit/no-secrets", git_repo, dry_run=True))
    assert code == 0
    assert not (git_repo / ".git" / "hooks" / "pre-commit").exists()


def test_install_writes_to_gitdir_hooks_when_dotgit_is_file(tmp_path):
    repo = tmp_path / "worktree"
    repo.mkdir()
    git_dir = tmp_path / "worktree-git"
    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(parents=True)
    (repo / ".git").write_text("gitdir: ../worktree-git\n")

    code = cmd_install(_args("pre-commit/no-secrets", repo))

    assert code == 0
    hook_file = hooks_dir / "pre-commit"
    assert hook_file.exists()
    assert is_executable(hook_file)
    assert "hookman: no-secrets" in hook_file.read_text()


def test_uninstall_removes_hook(git_repo):
    cmd_install(_args("pre-commit/no-secrets", git_repo))
    hook_file = git_repo / ".git" / "hooks" / "pre-commit"
    assert hook_file.exists()
    code = cmd_uninstall(SimpleNamespace(hook="pre-commit", path=str(git_repo), dry_run=False))
    assert code == 0
    assert not hook_file.exists()


def test_uninstall_missing_hook_is_noop(git_repo):
    code = cmd_uninstall(SimpleNamespace(hook="pre-push", path=str(git_repo), dry_run=False))
    assert code == 0


def test_install_one_outside_repo_returns_error(tmp_path):
    ok, msg = install_one("pre-commit/no-secrets", tmp_path)
    assert ok is False
    assert "git" in msg.lower()
