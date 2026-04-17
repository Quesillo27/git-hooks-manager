"""Tests de hooks builtin."""

import pytest

from hookman.hooks.builtins import BUILTIN_HOOKS, get_hook, list_hook_names


def test_builtins_not_empty():
    assert len(BUILTIN_HOOKS) >= 7


def test_each_hook_has_structure():
    for name, info in BUILTIN_HOOKS.items():
        assert "description" in info, f"Hook '{name}' sin descripción"
        assert "content" in info, f"Hook '{name}' sin contenido"
        assert info["content"].startswith("#!/bin/bash"), f"Hook '{name}' sin shebang bash"


def test_each_hook_has_hookman_signature():
    for name, info in BUILTIN_HOOKS.items():
        assert "# hookman:" in info["content"], f"Hook '{name}' sin firma hookman"


@pytest.mark.parametrize(
    "hook",
    [
        "pre-commit/no-secrets",
        "pre-commit/lint-python",
        "pre-commit/lint-js",
        "pre-commit/no-large-files",
        "commit-msg/conventional",
        "commit-msg/no-wip",
        "pre-push/run-tests",
        "pre-push/protect-branch",
        "post-commit/notify",
    ],
)
def test_expected_hooks_exist(hook):
    assert hook in BUILTIN_HOOKS


def test_get_hook_returns_definition():
    h = get_hook("pre-commit/no-secrets")
    assert h is not None
    assert "description" in h


def test_get_hook_returns_none_unknown():
    assert get_hook("pre-commit/nonexistent") is None


def test_list_hook_names_sorted():
    names = list_hook_names()
    assert names == sorted(names)
    assert "commit-msg/conventional" in names
