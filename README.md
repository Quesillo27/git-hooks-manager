# Git Hooks Manager

![Python](https://img.shields.io/badge/Python-3.8+-blue) ![License](https://img.shields.io/badge/license-MIT-green) ![Tests](https://img.shields.io/badge/tests-passing-brightgreen)

CLI Python para instalar, gestionar y deshabilitar git hooks de forma automática en cualquier repositorio. Incluye hooks prediseñados para verificación de credenciales, linting, Conventional Commits y ejecución de tests.

## Instalación en 3 comandos

```bash
git clone https://github.com/Quesillo27/git-hooks-manager
cd git-hooks-manager
pip install -r requirements.txt   # solo pytest para tests
```

## Uso

```bash
# Ver todos los hooks disponibles e instalados en el repo actual
python3 git_hooks_manager.py list

# Instalar todos los hooks
python3 git_hooks_manager.py install --all

# Instalar hooks específicos
python3 git_hooks_manager.py install pre-commit commit-msg

# Desinstalar un hook
python3 git_hooks_manager.py uninstall pre-push

# Deshabilitar temporalmente (sin eliminar)
python3 git_hooks_manager.py disable pre-commit

# Rehabilitar
python3 git_hooks_manager.py enable pre-commit

# Ver contenido de un hook
python3 git_hooks_manager.py show pre-commit

# Instalar hook personalizado desde un archivo
python3 git_hooks_manager.py add-custom pre-commit ./mi_hook.sh
```

## Ejemplo

```bash
cd /mi/proyecto-git
python3 /ruta/git_hooks_manager.py list
# ============================================
# 📂 Repo: /mi/proyecto-git
# 🪝  Hooks dir: /mi/proyecto-git/.git/hooks
#
# Hook                 Estado       Descripción
# ──────────────────────────────────────────────────────────────────────
# pre-commit           ✅ installed  Verifica sintaxis, linting y credenciales
# commit-msg           ⬜ available  Verifica formato Conventional Commits
# pre-push             ⬜ available  Ejecuta tests antes de hacer push
# post-merge           ⬜ available  Instala dependencias después de merge

python3 /ruta/git_hooks_manager.py install commit-msg
# ✅ Hook instalado: commit-msg
# 🎉 1 hook(s) instalado(s)
```

## Hooks disponibles

| Hook | Descripción |
|------|-------------|
| `pre-commit` | Detecta credenciales hardcodeadas, verifica sintaxis Python/JS |
| `commit-msg` | Valida formato [Conventional Commits](https://conventionalcommits.org) |
| `pre-push` | Ejecuta `npm test` o `make test` antes de push |
| `post-merge` | Reinstala dependencias si cambió `package.json` o `requirements.txt` |

## Variables de entorno

No requiere variables de entorno. El script es completamente portable.

## Opciones CLI

| Comando | Descripción |
|---------|-------------|
| `list` | Lista hooks disponibles e instalados |
| `install [hook...]` | Instala hook(s). Sin argumentos instala todos |
| `install --all` | Instala todos los hooks de la librería |
| `install --force` | Sobreescribe sin crear backup |
| `uninstall hook` | Elimina hook del repo |
| `disable hook` | Deshabilita hook temporalmente (renombra a .disabled) |
| `enable hook` | Rehabilita hook deshabilitado |
| `show hook` | Muestra el contenido del hook |
| `add-custom name file` | Instala hook personalizado desde archivo |
| `--path/-p DIR` | Especifica el repo (default: directorio actual) |

## Tests

```bash
make test
# ✅ Todos los tests pasaron (11/11)
```

## Contribuir

PRs bienvenidos. Corre `make test` antes de enviar. Para agregar un hook a la librería, agrega una entrada al diccionario `HOOKS_LIBRARY` en `git_hooks_manager.py`.
