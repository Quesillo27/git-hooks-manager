"""Tests para Git Hooks Manager."""

import os
import sys
import stat
import json
import tempfile
import subprocess
from pathlib import Path

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

import git_hooks_manager as ghm


def make_git_repo(tmp_path: Path) -> Path:
    """Crea un repo git de prueba."""
    repo = tmp_path / "test_repo"
    repo.mkdir()
    subprocess.run(["git", "init", str(repo)], capture_output=True, check=True)
    return repo


def test_find_git_root(tmp_path):
    repo = make_git_repo(tmp_path)
    subdir = repo / "src" / "utils"
    subdir.mkdir(parents=True)

    result = ghm.find_git_root(subdir)
    assert result == repo, f"Expected {repo}, got {result}"
    print("✅ find_git_root: PASS")


def test_find_git_root_not_git(tmp_path):
    result = ghm.find_git_root(tmp_path)
    assert result is None
    print("✅ find_git_root_not_git: PASS")


def test_hooks_library_structure():
    """Verifica que la librería de hooks tiene la estructura correcta."""
    for name, info in ghm.HOOKS_LIBRARY.items():
        assert "description" in info, f"Hook {name} no tiene 'description'"
        assert "content" in info, f"Hook {name} no tiene 'content'"
        assert info["content"].startswith("#!/bin/bash"), f"Hook {name} no tiene shebang"
    print(f"✅ hooks_library_structure: PASS ({len(ghm.HOOKS_LIBRARY)} hooks)")


def test_make_executable(tmp_path):
    test_file = tmp_path / "test_hook"
    test_file.write_text("#!/bin/bash\necho hello")

    # Asegurar que no es ejecutable
    test_file.chmod(0o644)
    assert not (test_file.stat().st_mode & stat.S_IXUSR)

    ghm.make_executable(test_file)
    assert test_file.stat().st_mode & stat.S_IXUSR
    print("✅ make_executable: PASS")


def test_load_config_no_file(tmp_path):
    repo = make_git_repo(tmp_path)
    config = ghm.load_config(repo)
    assert config == {"installed": [], "disabled": []}
    print("✅ load_config_no_file: PASS")


def test_save_and_load_config(tmp_path):
    repo = make_git_repo(tmp_path)
    config = {"installed": ["pre-commit"], "disabled": ["commit-msg"]}
    ghm.save_config(repo, config)

    loaded = ghm.load_config(repo)
    assert loaded == config
    print("✅ save_and_load_config: PASS")


def test_install_hook(tmp_path):
    repo = make_git_repo(tmp_path)
    hooks_dir = ghm.get_hooks_dir(repo)

    # Simular args
    class Args:
        path = str(repo)
        hooks = ["pre-commit"]
        all = False
        force = True

    ghm.cmd_install(Args())

    hook_path = hooks_dir / "pre-commit"
    assert hook_path.exists(), "Hook no fue creado"
    assert hook_path.stat().st_mode & stat.S_IXUSR, "Hook no es ejecutable"

    config = ghm.load_config(repo)
    assert "pre-commit" in config["installed"]
    print("✅ install_hook: PASS")


def test_uninstall_hook(tmp_path):
    repo = make_git_repo(tmp_path)
    hooks_dir = ghm.get_hooks_dir(repo)

    # Instalar primero
    class InstallArgs:
        path = str(repo)
        hooks = ["pre-commit"]
        all = False
        force = True

    ghm.cmd_install(InstallArgs())
    assert (hooks_dir / "pre-commit").exists()

    # Desinstalar
    class UninstallArgs:
        path = str(repo)
        hooks = ["pre-commit"]

    ghm.cmd_uninstall(UninstallArgs())
    assert not (hooks_dir / "pre-commit").exists()
    print("✅ uninstall_hook: PASS")


def test_disable_and_enable_hook(tmp_path):
    repo = make_git_repo(tmp_path)
    hooks_dir = ghm.get_hooks_dir(repo)

    # Instalar
    class InstallArgs:
        path = str(repo)
        hooks = ["commit-msg"]
        all = False
        force = True

    ghm.cmd_install(InstallArgs())

    # Deshabilitar
    class DisableArgs:
        path = str(repo)
        hook = "commit-msg"

    ghm.cmd_disable(DisableArgs())
    assert not (hooks_dir / "commit-msg").exists()
    assert (hooks_dir / "commit-msg.disabled").exists()

    config = ghm.load_config(repo)
    assert "commit-msg" in config["disabled"]

    # Habilitar de nuevo
    class EnableArgs:
        path = str(repo)
        hook = "commit-msg"

    ghm.cmd_enable(EnableArgs())
    assert (hooks_dir / "commit-msg").exists()
    assert not (hooks_dir / "commit-msg.disabled").exists()

    config = ghm.load_config(repo)
    assert "commit-msg" not in config["disabled"]
    print("✅ disable_and_enable_hook: PASS")


def test_add_custom_hook(tmp_path):
    repo = make_git_repo(tmp_path)
    hooks_dir = ghm.get_hooks_dir(repo)

    # Crear archivo de hook custom
    custom_hook = tmp_path / "my_hook.sh"
    custom_hook.write_text("#!/bin/bash\necho 'custom hook'")

    class Args:
        path = str(repo)
        hook_name = "post-commit"
        file = str(custom_hook)

    ghm.cmd_add_custom(Args())

    installed_hook = hooks_dir / "post-commit"
    assert installed_hook.exists()
    assert installed_hook.stat().st_mode & stat.S_IXUSR
    print("✅ add_custom_hook: PASS")


def test_smoke_import():
    """Smoke test: verificar que el módulo importa y tiene las funciones esperadas."""
    assert hasattr(ghm, "HOOKS_LIBRARY")
    assert hasattr(ghm, "cmd_install")
    assert hasattr(ghm, "cmd_uninstall")
    assert hasattr(ghm, "cmd_list")
    assert hasattr(ghm, "cmd_disable")
    assert hasattr(ghm, "cmd_enable")
    assert len(ghm.HOOKS_LIBRARY) >= 4
    print("✅ smoke_import: PASS")


if __name__ == "__main__":
    import tempfile

    print("🧪 Ejecutando tests de Git Hooks Manager...\n")
    errors = 0

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        tests = [
            test_smoke_import,
            test_hooks_library_structure,
            test_find_git_root,
            test_find_git_root_not_git,
            test_make_executable,
            test_load_config_no_file,
            test_save_and_load_config,
            test_install_hook,
            test_uninstall_hook,
            test_disable_and_enable_hook,
            test_add_custom_hook,
        ]

        for test in tests:
            try:
                if test.__code__.co_varnames and "tmp_path" in test.__code__.co_varnames[:1]:
                    with tempfile.TemporaryDirectory() as t:
                        test(Path(t))
                else:
                    test()
            except Exception as e:
                print(f"❌ {test.__name__}: FAIL — {e}")
                errors += 1

    print(f"\n{'='*50}")
    if errors == 0:
        print(f"✅ Todos los tests pasaron ({len(tests)}/{len(tests)})")
    else:
        print(f"❌ {errors} test(s) fallaron")
        sys.exit(1)
