"""Hooks integrados con hookman.

Cada hook tiene `description` y `content` (script bash). Las firmas en la
primera línea de comentario (`# hookman: <slug>`) sirven para detectar
duplicados al instalar.
"""

BUILTIN_HOOKS = {
    "pre-commit/no-secrets": {
        "description": "Previene commitear archivos con posibles secretos",
        "content": r"""#!/bin/bash
# hookman: no-secrets — Detecta posibles credenciales antes del commit
PATTERNS='password\s*=\s*['\''"][^'\''"$]\|secret\s*=\s*['\''"][^'\''"$]\|api[_-]?key\s*=\s*['\''"][^'\''"$]\|BEGIN RSA PRIVATE KEY\|BEGIN EC PRIVATE KEY\|BEGIN OPENSSH PRIVATE KEY'
FILES=$(git diff --cached --name-only --diff-filter=ACM)
FOUND=0
for FILE in $FILES; do
    if echo "$FILE" | grep -qiE '\.(env|pem|key|pfx|p12|cer|crt)$'; then
        echo "X Posible archivo de secretos: $FILE"
        FOUND=1
    fi
    if git show ":$FILE" 2>/dev/null | grep -qiE "$PATTERNS"; then
        echo "X Posible secreto en: $FILE"
        FOUND=1
    fi
done
if [ "$FOUND" -eq 1 ]; then
    echo "ERROR: commit bloqueado. Revisa los archivos indicados."
    exit 1
fi
exit 0
""",
    },
    "pre-commit/lint-python": {
        "description": "Ejecuta flake8 en archivos Python modificados",
        "content": r"""#!/bin/bash
# hookman: lint-python — Lintea archivos Python antes del commit
PY_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$')
if [ -z "$PY_FILES" ]; then exit 0; fi
if ! command -v flake8 >/dev/null 2>&1; then
    echo "WARN: flake8 no instalado — saltando lint Python"
    exit 0
fi
echo "Lintando Python..."
echo "$PY_FILES" | xargs flake8 --max-line-length=100
if [ $? -ne 0 ]; then
    echo "ERROR: errores de lint encontrados."
    exit 1
fi
exit 0
""",
    },
    "pre-commit/lint-js": {
        "description": "Ejecuta eslint en archivos JS/TS modificados",
        "content": r"""#!/bin/bash
# hookman: lint-js — Lintea archivos JS/TS antes del commit
JS_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(js|jsx|ts|tsx)$')
if [ -z "$JS_FILES" ]; then exit 0; fi
if ! command -v npx >/dev/null 2>&1; then exit 0; fi
if [ ! -f .eslintrc.js ] && [ ! -f .eslintrc.json ] && [ ! -f .eslintrc.yml ] && [ ! -f eslint.config.js ] && ! grep -q '"eslintConfig"' package.json 2>/dev/null; then
    echo "WARN: ESLint no configurado — saltando lint JS"
    exit 0
fi
echo "Lintando JS/TS..."
echo "$JS_FILES" | xargs npx eslint --no-error-on-unmatched-pattern
if [ $? -ne 0 ]; then
    echo "ERROR: errores de ESLint."
    exit 1
fi
exit 0
""",
    },
    "pre-commit/no-large-files": {
        "description": "Previene commitear archivos mayores a 1MB",
        "content": r"""#!/bin/bash
# hookman: no-large-files — Bloquea archivos grandes (>1MB)
MAX_SIZE=${HOOKMAN_MAX_FILE_BYTES:-1048576}
FILES=$(git diff --cached --name-only --diff-filter=ACM)
FOUND=0
for FILE in $FILES; do
    if [ -f "$FILE" ]; then
        SIZE=$(wc -c < "$FILE")
        if [ "$SIZE" -gt "$MAX_SIZE" ]; then
            echo "X Archivo demasiado grande: $FILE ($(( SIZE / 1024 ))KB)"
            FOUND=1
        fi
    fi
done
if [ "$FOUND" -eq 1 ]; then
    echo "ERROR: usa Git LFS para archivos grandes."
    exit 1
fi
exit 0
""",
    },
    "commit-msg/conventional": {
        "description": "Valida formato de Conventional Commits",
        "content": r"""#!/bin/bash
# hookman: conventional-commits — Valida formato de commit message
COMMIT_MSG=$(head -n1 "$1")
PATTERN='^(feat|fix|docs|style|refactor|perf|test|chore|ci|build|revert)(\(.+\))?!?: .{3,}'
if ! echo "$COMMIT_MSG" | grep -qE "$PATTERN"; then
    echo "ERROR: commit message inválido."
    echo "  Formato esperado: <tipo>(scope?): descripción"
    echo "  Tipos válidos: feat|fix|docs|style|refactor|perf|test|chore|ci|build|revert"
    echo "  Ejemplo: feat(auth): add JWT refresh token"
    exit 1
fi
exit 0
""",
    },
    "commit-msg/no-wip": {
        "description": "Bloquea commits con WIP/FIXUP en el mensaje",
        "content": r"""#!/bin/bash
# hookman: no-wip — Bloquea commits con WIP o FIXUP
COMMIT_MSG=$(cat "$1")
if echo "$COMMIT_MSG" | grep -qiE '^(wip|fixup!|squash!)\b'; then
    echo "ERROR: commits WIP/FIXUP no permitidos. Usa git rebase -i."
    exit 1
fi
exit 0
""",
    },
    "pre-push/run-tests": {
        "description": "Ejecuta npm test, pytest o make test antes de push",
        "content": r"""#!/bin/bash
# hookman: run-tests — Ejecuta tests antes del push
if [ -f package.json ] && grep -q '"test"' package.json; then
    echo "Ejecutando npm test..."
    npm test
    [ $? -ne 0 ] && exit 1
elif [ -f requirements.txt ] || [ -f pyproject.toml ]; then
    if command -v pytest >/dev/null 2>&1; then
        echo "Ejecutando pytest..."
        pytest --tb=short -q
        [ $? -ne 0 ] && exit 1
    fi
elif [ -f Makefile ] && grep -q '^test:' Makefile; then
    echo "Ejecutando make test..."
    make test
    [ $? -ne 0 ] && exit 1
fi
exit 0
""",
    },
    "pre-push/protect-branch": {
        "description": "Bloquea push directo a main/master",
        "content": r"""#!/bin/bash
# hookman: protect-branch — Bloquea push a ramas protegidas
PROTECTED='^(main|master|production|prod)$'
BRANCH=$(git rev-parse --abbrev-ref HEAD)
if echo "$BRANCH" | grep -qE "$PROTECTED"; then
    echo "ERROR: push directo a '$BRANCH' bloqueado. Usa Pull Request."
    exit 1
fi
exit 0
""",
    },
    "post-commit/notify": {
        "description": "Muestra resumen del commit al terminar",
        "content": r"""#!/bin/bash
# hookman: notify — Muestra resumen del commit
COMMIT=$(git log -1 --format='%h %s' HEAD)
BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "[OK] Commit en [$BRANCH]: $COMMIT"
""",
    },
}


def get_hook(name: str):
    """Devuelve la definición del hook builtin o None."""
    return BUILTIN_HOOKS.get(name)


def list_hook_names() -> list:
    """Lista los nombres de todos los hooks builtin."""
    return sorted(BUILTIN_HOOKS.keys())
