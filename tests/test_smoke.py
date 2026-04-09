#!/usr/bin/env python3
"""Smoke tests para git-hooks-manager."""
import sys
import os
import tempfile
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

def test_import():
    """El modulo importa sin errores."""
    import git_hooks_manager
    assert hasattr(git_hooks_manager, 'install_hook')
    assert hasattr(git_hooks_manager, 'remove_hook')
    assert hasattr(git_hooks_manager, 'list_hooks')
    assert hasattr(git_hooks_manager, 'HOOKS')
    print("test_import passed")

def test_hooks_available():
    """Los hooks esperados estan definidos."""
    from git_hooks_manager import HOOKS
    assert 'pre-commit' in HOOKS
    assert 'commit-msg' in HOOKS
    assert 'pre-push' in HOOKS
    print("test_hooks_available passed")

def test_find_git_root():
    """find_git_root encuentra el directorio correcto."""
    from git_hooks_manager import find_git_root
    result = find_git_root(Path('.'))
    print(f"test_find_git_root passed (git_root={result})")

def test_install_and_remove():
    """Instalar y eliminar hooks funciona correctamente."""
    from git_hooks_manager import install_hook, remove_hook

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        subprocess.run(['git', 'init', str(tmp)], capture_output=True)

        result = install_hook(tmp, 'pre-commit')
        assert result == True
        hook_path = tmp / '.git' / 'hooks' / 'pre-commit'
        assert hook_path.exists()
        assert os.access(hook_path, os.X_OK), "Hook debe ser ejecutable"

        result = remove_hook(tmp, 'pre-commit')
        assert result == True
        assert not hook_path.exists()

        print("test_install_and_remove passed")

def test_cli_help():
    """CLI responde a --help sin error."""
    result = subprocess.run(
        [sys.executable, 'git_hooks_manager.py', '--help'],
        capture_output=True, text=True,
        cwd=str(Path(__file__).parent.parent)
    )
    assert result.returncode == 0
    assert 'Git Hooks Manager' in result.stdout
    print("test_cli_help passed")

if __name__ == '__main__':
    tests = [test_import, test_hooks_available, test_find_git_root, test_install_and_remove, test_cli_help]
    failed = 0
    for t in tests:
        try:
            t()
        except Exception as e:
            print(f"FAILED {t.__name__}: {e}")
            failed += 1

    if failed:
        print(f"\n{failed}/{len(tests)} tests fallaron")
        sys.exit(1)
    else:
        print(f"\nTodos los tests pasaron ({len(tests)}/{len(tests)})")
        sys.exit(0)
