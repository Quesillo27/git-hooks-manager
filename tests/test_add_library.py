"""Tests de add (librería personalizada)."""

from types import SimpleNamespace

from hookman.commands.add_cmd import cmd_add_to_library
from hookman.commands.install_cmd import cmd_install
from hookman.config import HOOKS_LIBRARY


def test_add_custom_hook_to_library(tmp_path):
    src = tmp_path / "my-check.sh"
    src.write_text("#!/bin/bash\necho custom\n")
    code = cmd_add_to_library(
        SimpleNamespace(file=str(src), type="pre-commit", name="my-check")
    )
    assert code == 0
    dest = HOOKS_LIBRARY / "pre-commit" / "my-check.sh"
    assert dest.exists()
    assert "custom" in dest.read_text()


def test_add_missing_file_fails():
    code = cmd_add_to_library(
        SimpleNamespace(file="/does/not/exist.sh", type="pre-commit", name="x")
    )
    assert code == 1


def test_add_invalid_type(tmp_path):
    src = tmp_path / "h.sh"
    src.write_text("#!/bin/bash\n")
    code = cmd_add_to_library(
        SimpleNamespace(file=str(src), type="not-a-hook", name="h")
    )
    assert code == 1


def test_add_without_shebang_fails(tmp_path):
    src = tmp_path / "bad.sh"
    src.write_text("echo missing shebang\n")
    code = cmd_add_to_library(
        SimpleNamespace(file=str(src), type="pre-commit", name="bad")
    )
    assert code == 1


def test_install_custom_hook_from_library(tmp_path, git_repo):
    src = tmp_path / "team-lint.sh"
    src.write_text("#!/bin/bash\necho team\nexit 0\n")
    cmd_add_to_library(
        SimpleNamespace(file=str(src), type="pre-commit", name="team-lint")
    )
    code = cmd_install(
        SimpleNamespace(
            hook="pre-commit/team-lint",
            path=str(git_repo),
            force=False,
            dry_run=False,
        )
    )
    assert code == 0
    installed = git_repo / ".git" / "hooks" / "pre-commit"
    assert installed.exists()
    assert "team" in installed.read_text()
