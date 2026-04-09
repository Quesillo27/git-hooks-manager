# hookman — Git Hooks Manager

![Python](https://img.shields.io/badge/python-3.8%2B-blue) ![License](https://img.shields.io/badge/license-MIT-green) ![Tests](https://img.shields.io/badge/tests-pytest-orange)

Instala, gestiona y sincroniza git hooks entre proyectos. Incluye hooks integrados para seguridad, linting y convenciones de commits. Sin dependencias externas.

## Instalación en 3 comandos

```bash
git clone https://github.com/Quesillo27/git-hooks-manager
cd git-hooks-manager
pip install -e .
```

## Uso

```bash
hookman list                          # ver hooks disponibles
hookman install pre-commit/no-secrets # instalar hook de seguridad
hookman profile nodejs                # aplicar perfil completo Node.js
hookman status                        # ver hooks instalados en repo actual
```

## Hooks integrados

| Hook | Tipo | Descripción |
|---|---|---|
| `no-secrets` | pre-commit | Bloquea archivos con posibles credenciales |
| `lint-python` | pre-commit | Ejecuta flake8 en archivos Python |
| `lint-js` | pre-commit | Ejecuta ESLint en archivos JS/TS |
| `no-large-files` | pre-commit | Bloquea archivos >1MB |
| `conventional` | commit-msg | Valida formato Conventional Commits |
| `run-tests` | pre-push | Ejecuta npm test o pytest antes del push |
| `notify` | post-commit | Muestra resumen del commit |

## Perfiles disponibles

```bash
hookman profile basic    # no-secrets + conventional-commits
hookman profile python   # lint + tests + conventional + no-secrets
hookman profile nodejs   # eslint + tests + conventional + no-secrets
hookman profile strict   # todo lo anterior + no-large-files
```

## Ejemplos

```bash
# Instalar hook de Conventional Commits en el repo actual
cd mi-proyecto
hookman install commit-msg/conventional
# → ✅ Hook instalado en mi-proyecto/.git/hooks/commit-msg

# Ver qué hooks están activos
hookman status
# → ✅ commit-msg   (247 bytes)
# → ✅ pre-commit   (521 bytes)

# Sincronizar hooks de un repo a otro
hookman sync ./proyecto-a ./proyecto-b
# → ✅ 3 hook(s) sincronizados

# Agregar hook personalizado a la librería
hookman add mi-hook.sh --type pre-commit --name check-todos
```

## Comandos disponibles

| Comando | Descripción |
|---|---|
| `list` | Lista todos los hooks disponibles |
| `install <hook>` | Instala un hook en el repo actual |
| `uninstall <tipo>` | Elimina un hook del repo actual |
| `status [path]` | Muestra hooks instalados |
| `profile <nombre>` | Aplica un perfil de hooks |
| `add <file>` | Agrega script personalizado a la librería |
| `sync <src> <dst>` | Copia hooks entre repos |

## Variables / Configuración

Los perfiles personalizados se guardan en `~/.hookman/profiles.json`. Los hooks personalizados en `~/.hookman/library/`.

## Contribuir

```bash
make install   # instalar dependencias de dev
make test      # correr tests
make lint      # verificar código
```

PRs bienvenidos. Asegúrate de que `make test` pasa antes de enviar.
