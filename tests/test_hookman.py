"""Tests básicos para hookman"""
import sys
import os
import subprocess
import tempfile
import pytest
from pathlib import Path

# Agregar raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))
import hookman


def test_version():
    """El módulo tiene VERSION definida"""
    assert hookman.VERSION is not None
    assert len(hookman.VERSION) > 0


def test_builtin_hooks_structure():
    """Los hooks integrados tienen la estructura correcta"""
    for name, info in hookman.BUILTIN_HOOKS.items():
        assert "description" in info, f"Hook '{name}' sin descripción"
        assert "content" in info, f"Hook '{name}' sin contenido"
        assert "#!/bin/bash" in info["content"], f"Hook '{name}' sin shebang"


def test_valid_hooks_list():
    """La lista de hooks válidos incluye los más comunes"""
    assert "pre-commit" in hookman.VALID_HOOKS
    assert "commit-msg" in hookman.VALID_HOOKS
    assert "pre-push" in hookman.VALID_HOOKS


def test_find_git_root_no_repo():
    """find_git_root retorna None fuera de un repo"""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = hookman.find_git_root(Path(tmpdir))
        assert result is None


def test_find_git_root_with_repo():
    """find_git_root encuentra el .git"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        (tmppath / ".git").mkdir()
        result = hookman.find_git_root(tmppath)
        assert result == tmppath


def test_hook_type_extraction():
    """hook_type extrae correctamente el tipo"""
    assert hookman.hook_type("pre-commit/no-secrets") == "pre-commit"
    assert hookman.hook_type("commit-msg/conventional") == "commit-msg"
    assert hookman.hook_type("pre-push/run-tests") == "pre-push"


def test_cli_help():
    """El CLI responde a --help sin errores"""
    result = subprocess.run(
        [sys.executable, "hookman.py", "--help"],
        capture_output=True, text=True, cwd=Path(__file__).parent.parent
    )
    assert result.returncode == 0
    assert "hookman" in result.stdout.lower()


def test_cli_list():
    """El comando list funciona"""
    result = subprocess.run(
        [sys.executable, "hookman.py", "list"],
        capture_output=True, text=True, cwd=Path(__file__).parent.parent
    )
    assert result.returncode == 0
    assert "pre-commit" in result.stdout
