"""Tests de perfiles."""

import json
from types import SimpleNamespace

import pytest

from hookman.commands.export_cmd import cmd_export_profile
from hookman.commands.profile_cmd import cmd_apply_profile
from hookman.hooks.profiles import (
    create_profile,
    delete_profile,
    get_all_profiles,
    load_profiles,
)


def test_profile_basic_installs_two_hooks(git_repo):
    code = cmd_apply_profile(
        SimpleNamespace(profile="basic", path=str(git_repo), force=False, dry_run=False)
    )
    assert code == 0
    assert (git_repo / ".git" / "hooks" / "pre-commit").exists()
    assert (git_repo / ".git" / "hooks" / "commit-msg").exists()


def test_profile_full_installs_multiple_types(git_repo):
    code = cmd_apply_profile(
        SimpleNamespace(profile="full", path=str(git_repo), force=False, dry_run=False)
    )
    assert code == 0
    assert (git_repo / ".git" / "hooks" / "pre-commit").exists()
    assert (git_repo / ".git" / "hooks" / "commit-msg").exists()
    assert (git_repo / ".git" / "hooks" / "pre-push").exists()
    assert (git_repo / ".git" / "hooks" / "post-commit").exists()


def test_unknown_profile_fails(git_repo):
    code = cmd_apply_profile(
        SimpleNamespace(profile="does-not-exist", path=str(git_repo), force=False, dry_run=False)
    )
    assert code == 1


def test_create_and_delete_custom_profile():
    create_profile("my-team", ["pre-commit/no-secrets", "pre-push/run-tests"])
    profiles = load_profiles()["profiles"]
    assert "my-team" in profiles
    assert profiles["my-team"] == ["pre-commit/no-secrets", "pre-push/run-tests"]

    assert delete_profile("my-team") is True
    assert delete_profile("my-team") is False


def test_create_profile_validates_args():
    with pytest.raises(ValueError):
        create_profile("", ["pre-commit/no-secrets"])
    with pytest.raises(ValueError):
        create_profile("x", [])


def test_get_all_profiles_merges_user_and_builtin():
    create_profile("team-custom", ["pre-commit/no-secrets"])
    all_p = get_all_profiles()
    assert "basic" in all_p
    assert "team-custom" in all_p


def test_export_profile_to_stdout(capsys):
    cmd_export_profile(SimpleNamespace(profile="basic", output=None))
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["profile"] == "basic"
    assert "pre-commit/no-secrets" in data["hooks"]


def test_export_profile_to_file(tmp_path):
    dest = tmp_path / "exported.json"
    code = cmd_export_profile(SimpleNamespace(profile="strict", output=str(dest)))
    assert code == 0
    data = json.loads(dest.read_text())
    assert data["profile"] == "strict"
    assert len(data["hooks"]) >= 3


def test_export_unknown_profile_fails():
    code = cmd_export_profile(SimpleNamespace(profile="nope", output=None))
    assert code == 1
