# git-hooks-manager

CLI Python para instalar y gestionar git hooks automaticamente en proyectos.

## Instalacion rapida

```bash
git clone https://github.com/Quesillo27/git-hooks-manager.git
cd git-hooks-manager
python git_hooks_manager.py install all
```

## Uso

```bash
# Instalar todos los hooks
python git_hooks_manager.py install all

# Instalar un hook especifico
python git_hooks_manager.py install pre-commit

# Sobrescribir hook existente
python git_hooks_manager.py install pre-commit --force

# Eliminar un hook
python git_hooks_manager.py remove commit-msg

# Listar estado de hooks
python git_hooks_manager.py list

# Operar en otro directorio
python git_hooks_manager.py --path /otro/repo list
```

## Hooks disponibles

| Hook | Descripcion |
|------|-------------|
| `pre-commit` | Verifica syntax Python y lint JS (si hay npm script) |
| `commit-msg` | Valida que el mensaje tenga minimo 10 caracteres |
| `pre-push` | Corre tests antes de push (npm test o make test) |

## Requisitos

- Python 3.8+
- Sin dependencias externas (solo stdlib)

## Tests

```bash
python tests/test_smoke.py
```
