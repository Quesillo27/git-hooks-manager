"""Comando `hookman list` — lista hooks disponibles."""

from types import SimpleNamespace

from hookman.config import HOOKS_LIBRARY, ensure_hookman_dir
from hookman.hooks.builtins import BUILTIN_HOOKS
from hookman.utils import hook_type


def cmd_list(args: SimpleNamespace = None) -> int:
    """Imprime todos los hooks builtin y personalizados agrupados por tipo."""
    ensure_hookman_dir()
    json_output = bool(getattr(args, "json", False)) if args else False

    if json_output:
        import json

        by_type: dict = {}
        for name, info in BUILTIN_HOOKS.items():
            by_type.setdefault(hook_type(name), []).append(
                {"name": name, "description": info["description"]}
            )
        custom = sorted(str(f.relative_to(HOOKS_LIBRARY)) for f in HOOKS_LIBRARY.rglob("*.sh"))
        print(json.dumps({"builtin": by_type, "custom": custom}, indent=2, sort_keys=True))
        return 0

    print("\n" + "-" * 60)
    print(f"  Hooks integrados ({len(BUILTIN_HOOKS)} disponibles)")
    print("-" * 60)

    by_type: dict = {}
    for name, info in BUILTIN_HOOKS.items():
        by_type.setdefault(hook_type(name), []).append((name, info))

    for htype, hooks in sorted(by_type.items()):
        print(f"\n  [{htype}]")
        for name, info in hooks:
            short_name = name.split("/", 1)[1] if "/" in name else name
            print(f"    - {short_name:<25} {info['description']}")

    custom = sorted(HOOKS_LIBRARY.rglob("*.sh"))
    if custom:
        print(f"\n  Hooks personalizados ({len(custom)}):")
        for f in custom:
            rel = f.relative_to(HOOKS_LIBRARY)
            print(f"    - {rel}")

    print()
    return 0
