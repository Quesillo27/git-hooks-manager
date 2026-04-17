"""Tests del comando init (autodetect de perfil)."""

from types import SimpleNamespace

from hookman.commands.init_cmd import cmd_init, _detect_project_type


def test_detect_basic(git_repo):
    assert _detect_project_type(git_repo) == "basic"


def test_detect_python(git_repo):
    (git_repo / "requirements.txt").write_text("")
    assert _detect_project_type(git_repo) == "python"


def test_detect_python_pyproject(git_repo):
    (git_repo / "pyproject.toml").write_text("[project]\n")
    assert _detect_project_type(git_repo) == "python"


def test_detect_nodejs(git_repo):
    (git_repo / "package.json").write_text('{"name":"x"}')
    assert _detect_project_type(git_repo) == "nodejs"


def test_init_installs_hooks(git_repo):
    (git_repo / "requirements.txt").write_text("")
    code = cmd_init(
        SimpleNamespace(path=str(git_repo), profile=None, force=False, dry_run=False)
    )
    assert code == 0
    assert (git_repo / ".git" / "hooks" / "pre-commit").exists()
    assert (git_repo / ".git" / "hooks" / "commit-msg").exists()


def test_init_with_explicit_profile(git_repo):
    code = cmd_init(
        SimpleNamespace(path=str(git_repo), profile="strict", force=False, dry_run=False)
    )
    assert code == 0
    assert (git_repo / ".git" / "hooks" / "pre-commit").exists()


def test_init_outside_repo(tmp_path):
    code = cmd_init(
        SimpleNamespace(path=str(tmp_path), profile=None, force=False, dry_run=False)
    )
    assert code == 1
