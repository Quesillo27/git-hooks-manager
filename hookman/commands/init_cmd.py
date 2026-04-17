"""Comando `hookman init` — inicializa un repo con un set recomendado."""

from pathlib import Path
from types import SimpleNamespace

from hookman.commands.profile_cmd import cmd_apply_profile
from hookman.utils import find_git_root


def _detect_project_type(repo: Path) -> str:
    """Detecta el tipo de proyecto para elegir un perfil inicial."""
    if (repo / "package.json").exists():
        return "nodejs"
    if (repo / "requirements.txt").exists() or (repo / "pyproject.toml").exists():
        return "python"
    return "basic"


def cmd_init(args: SimpleNamespace) -> int:
    """Aplica automáticamente el perfil apropiado al repo."""
    repo = find_git_root(Path(getattr(args, "path", ".") or "."))
    if not repo:
        print("ERROR: no estás dentro de un repositorio git")
        return 1

    profile_name = getattr(args, "profile", None) or _detect_project_type(repo)
    print(f"OK: inicializando '{repo.name}' con perfil '{profile_name}'")

    ns = SimpleNamespace(
        profile=profile_name,
        path=str(repo),
        force=bool(getattr(args, "force", False)),
        dry_run=bool(getattr(args, "dry_run", False)),
    )
    return cmd_apply_profile(ns)
