"""Punto de entrada CLI de hookman."""

import argparse
import sys
from typing import List, Optional

from hookman.config import VERSION, ensure_hookman_dir
from hookman.logger import get_logger
from hookman.commands import (
    cmd_add_to_library,
    cmd_apply_profile,
    cmd_disable,
    cmd_enable,
    cmd_export_profile,
    cmd_init,
    cmd_install,
    cmd_list,
    cmd_status,
    cmd_sync,
    cmd_uninstall,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hookman",
        description="Git Hooks Manager — instala y gestiona git hooks.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  hookman list
  hookman install pre-commit/no-secrets
  hookman profile nodejs
  hookman status
  hookman disable pre-commit
  hookman enable pre-commit
  hookman init
  hookman export-profile strict > strict.json
  hookman sync ./proyecto-a ./proyecto-b
""",
    )
    parser.add_argument("--version", action="version", version=f"hookman {VERSION}")
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Output detallado (logger a DEBUG)",
    )
    sub = parser.add_subparsers(dest="command", metavar="<comando>")

    p_list = sub.add_parser("list", help="Lista hooks disponibles")
    p_list.add_argument("--json", action="store_true", help="Salida JSON")
    p_list.set_defaults(func=cmd_list)

    p_install = sub.add_parser("install", help="Instala un hook")
    p_install.add_argument("hook", help="Ej: pre-commit/no-secrets")
    p_install.add_argument("--path", default=".", help="Ruta al repo")
    p_install.add_argument("--force", action="store_true", help="Sobrescribir existente")
    p_install.add_argument("--dry-run", action="store_true", help="Simular sin escribir")
    p_install.set_defaults(func=cmd_install)

    p_uninstall = sub.add_parser("uninstall", help="Elimina un hook")
    p_uninstall.add_argument("hook")
    p_uninstall.add_argument("--path", default=".")
    p_uninstall.add_argument("--dry-run", action="store_true")
    p_uninstall.set_defaults(func=cmd_uninstall)

    p_status = sub.add_parser("status", help="Hooks instalados en el repo")
    p_status.add_argument("path", nargs="?", default=".")
    p_status.add_argument("--json", action="store_true", help="Salida JSON")
    p_status.set_defaults(func=cmd_status)

    p_profile = sub.add_parser("profile", help="Aplica un perfil de hooks")
    p_profile.add_argument("profile", help="python|nodejs|basic|strict|full o custom")
    p_profile.add_argument("--path", default=".")
    p_profile.add_argument("--force", action="store_true")
    p_profile.add_argument("--dry-run", action="store_true")
    p_profile.set_defaults(func=cmd_apply_profile)

    p_add = sub.add_parser("add", help="Agrega script custom a la librería")
    p_add.add_argument("file")
    p_add.add_argument("--type", default="pre-commit")
    p_add.add_argument("--name")
    p_add.set_defaults(func=cmd_add_to_library)

    p_sync = sub.add_parser("sync", help="Copia hooks entre repos")
    p_sync.add_argument("source")
    p_sync.add_argument("destination")
    p_sync.set_defaults(func=cmd_sync)

    p_disable = sub.add_parser("disable", help="Deshabilita un hook (sin borrarlo)")
    p_disable.add_argument("hook")
    p_disable.add_argument("--path", default=".")
    p_disable.set_defaults(func=cmd_disable)

    p_enable = sub.add_parser("enable", help="Reactiva un hook deshabilitado")
    p_enable.add_argument("hook")
    p_enable.add_argument("--path", default=".")
    p_enable.set_defaults(func=cmd_enable)

    p_init = sub.add_parser("init", help="Autoinstala perfil recomendado según el repo")
    p_init.add_argument("--path", default=".")
    p_init.add_argument("--profile", help="Perfil específico (default: autodetect)")
    p_init.add_argument("--force", action="store_true")
    p_init.add_argument("--dry-run", action="store_true")
    p_init.set_defaults(func=cmd_init)

    p_export = sub.add_parser("export-profile", help="Exporta un perfil a JSON")
    p_export.add_argument("profile")
    p_export.add_argument("--output", "-o", help="Archivo destino (default: stdout)")
    p_export.set_defaults(func=cmd_export_profile)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    ensure_hookman_dir()
    parser = build_parser()
    args = parser.parse_args(argv)

    if getattr(args, "verbose", False):
        get_logger("DEBUG")

    if not getattr(args, "command", None):
        parser.print_help()
        return 0

    return int(args.func(args) or 0)


if __name__ == "__main__":
    sys.exit(main())
