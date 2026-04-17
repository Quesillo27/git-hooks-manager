# git-hooks-manager

![python](https://img.shields.io/badge/python-3.8+-blue)
![tests](https://img.shields.io/badge/tests-91%20passing-brightgreen)
![license](https://img.shields.io/badge/license-MIT-green)

CLI Python modular para instalar, gestionar y sincronizar git hooks entre proyectos.
Sin dependencias externas (solo stdlib).

## Instalación en 3 comandos

```bash
git clone https://github.com/Quesillo27/git-hooks-manager.git
cd git-hooks-manager
pip install -e .
```

Desde ese momento `hookman` está en tu PATH. También puedes ejecutar sin instalar:

```bash
python -m hookman <comando>
python hookman.py <comando>         # legacy
python git_hooks_manager.py <comando>  # legacy (compat con README v1)
```

## Uso rápido

```bash
# Listar hooks builtin
hookman list
hookman list --json

# Instalar un hook específico en el repo actual
hookman install pre-commit/no-secrets

# Inicializar un repo con un perfil autodetectado (python|nodejs|basic)
hookman init

# Aplicar un perfil explícito
hookman profile strict

# Ver estado de los hooks del repo
hookman status
hookman status --json

# Deshabilitar/reactivar sin borrar
hookman disable pre-commit
hookman enable pre-commit

# Sincronizar entre repos
hookman sync ./repo-a ./repo-b

# Exportar un perfil
hookman export-profile strict --output strict.json

# Ayuda
hookman --help
hookman install --help
```

## Hooks integrados

| Nombre | Tipo | Descripción |
|---|---|---|
| `no-secrets` | `pre-commit` | Detecta credenciales/claves en archivos staged |
| `lint-python` | `pre-commit` | Corre `flake8` en archivos `.py` modificados |
| `lint-js` | `pre-commit` | Corre `eslint` en archivos `.js/.ts` modificados |
| `no-large-files` | `pre-commit` | Bloquea archivos >1MB (configurable con `HOOKMAN_MAX_FILE_BYTES`) |
| `conventional` | `commit-msg` | Valida formato Conventional Commits |
| `no-wip` | `commit-msg` | Rechaza commits WIP/FIXUP |
| `run-tests` | `pre-push` | Corre npm test / pytest / make test antes del push |
| `protect-branch` | `pre-push` | Bloquea push directo a main/master/production |
| `notify` | `post-commit` | Muestra resumen del commit al terminar |

## Perfiles integrados

| Perfil | Hooks incluidos |
|---|---|
| `basic` | `no-secrets` + `conventional` |
| `python` | `no-secrets` + `lint-python` + `conventional` + `run-tests` |
| `nodejs` | `no-secrets` + `lint-js` + `conventional` + `run-tests` |
| `strict` | `no-secrets` + `no-large-files` + `conventional` + `run-tests` |
| `full` | todos los anteriores + `notify` |

## Hooks personalizados

Agrega scripts propios a la librería global (`~/.hookman/library/`):

```bash
hookman add mi_hook.sh --type pre-commit --name team-lint
hookman install pre-commit/team-lint
```

Perfiles personalizados se crean vía API:

```python
from hookman.hooks.profiles import create_profile
create_profile("mi-team", ["pre-commit/no-secrets", "pre-push/run-tests"])
```

## Variables de entorno

| Variable | Default | Descripción |
|---|---|---|
| `HOOKMAN_HOME` | `~/.hookman` | Directorio raíz donde viven profiles y librería |
| `HOOKMAN_LOG_LEVEL` | `INFO` | DEBUG / INFO / WARNING / ERROR |
| `HOOKMAN_MAX_FILE_BYTES` | `1048576` | Tamaño máximo permitido por `no-large-files` |

## Arquitectura

```
hookman/
├── __init__.py       # API pública
├── __main__.py       # python -m hookman
├── cli.py            # argparse + entry point
├── config.py         # rutas, versión, perfiles builtin
├── logger.py         # logger estructurado con niveles
├── utils.py          # find_git_root, hook_type, make_executable
├── hooks/
│   ├── builtins.py   # BUILTIN_HOOKS (9 hooks)
│   └── profiles.py   # carga/guarda perfiles JSON
└── commands/
    ├── list_cmd.py
    ├── install_cmd.py
    ├── uninstall_cmd.py
    ├── status_cmd.py
    ├── profile_cmd.py
    ├── add_cmd.py
    ├── sync_cmd.py
    ├── disable_cmd.py   # disable + enable
    ├── init_cmd.py      # autodetect perfil
    └── export_cmd.py
hookman.py            # shim legacy (re-exporta paquete)
git_hooks_manager.py  # shim legacy v1 (3 hooks clásicos)
```

## Tests

```bash
python -m pytest tests/ -v
# o
make test
```

91 tests unitarios + de integración (100% pass). Cada test usa fixture
`isolated_hookman_home` para no tocar `~/.hookman` real.

## Desarrollo

```bash
# Setup
pip install -e .[dev]

# Run tests con cobertura
make test

# Lint
make lint
```

## Roadmap

- [ ] Packaging como wheel en PyPI
- [ ] Integración con pre-commit framework (opcional, como alternativa)
- [ ] Dashboard web para ver hooks instalados en múltiples repos
- [ ] Distribución vía `pipx install hookman-cli`
- [ ] Hooks específicos para Go, Rust, Java (lint en pre-commit)
- [ ] CI/CD: GitHub Actions workflow que instale hooks automáticamente

## Requisitos

- Python 3.8+
- Git

## Licencia

MIT
