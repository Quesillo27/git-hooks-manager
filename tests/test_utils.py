"""Tests de hookman.utils."""

import stat

from hookman.utils import (
    find_git_root,
    get_hooks_dir,
    hook_short_name,
    hook_type,
    is_executable,
    make_executable,
)


def test_hook_type_extracts_prefix():
    assert hook_type("pre-commit/no-secrets") == "pre-commit"
    assert hook_type("commit-msg/conventional") == "commit-msg"
    assert hook_type("post-commit") == "post-commit"


def test_hook_short_name():
    assert hook_short_name("pre-commit/no-secrets") == "no-secrets"
    assert hook_short_name("pre-commit") == "pre-commit"


def test_find_git_root_no_repo(tmp_path):
    assert find_git_root(tmp_path) is None


def test_find_git_root_with_git_dir(tmp_path):
    (tmp_path / ".git").mkdir()
    assert find_git_root(tmp_path) == tmp_path.resolve()


def test_find_git_root_from_subdir(git_repo):
    sub = git_repo / "src" / "utils"
    sub.mkdir(parents=True)
    assert find_git_root(sub) == git_repo.resolve()


def test_get_hooks_dir(git_repo):
    assert get_hooks_dir(git_repo) == git_repo / ".git" / "hooks"


def test_make_executable_sets_exec_bits(tmp_path):
    f = tmp_path / "script.sh"
    f.write_text("#!/bin/bash\necho hi")
    f.chmod(0o644)
    assert not (f.stat().st_mode & stat.S_IXUSR)
    make_executable(f)
    mode = f.stat().st_mode
    assert mode & stat.S_IXUSR
    assert mode & stat.S_IXGRP
    assert mode & stat.S_IXOTH


def test_is_executable(tmp_path):
    f = tmp_path / "f.sh"
    f.write_text("#!/bin/sh\n")
    f.chmod(0o644)
    assert not is_executable(f)
    make_executable(f)
    assert is_executable(f)


def test_is_executable_missing(tmp_path):
    assert not is_executable(tmp_path / "nope")
