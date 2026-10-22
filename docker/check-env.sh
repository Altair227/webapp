#!/bin/sh
# Prepares and validates app/.env before containers start.
#
#   check-env.sh <env_file> <default_env_file> [--create-only]
#
# 1. Copies <default_env_file> to <env_file> when it is missing.
# 2. Sets LOG_DIR=/var/log/webapp when it is empty or absent.
# 3. Fails with instructions when a required variable is empty.
# --create-only does step 1 only (enough for `down`, `logs`...).

set -eu

ENV_FILE=$1
DEFAULT_FILE=$2
MODE=${3:-}

REQUIRED="POSTGRES_USER POSTGRES_PASSWORD POSTGRES_DB POSTGRES_HOST POSTGRES_PORT SECRET_KEY"
DEFAULT_LOG_DIR=/var/log/webapp

if [ ! -f "$ENV_FILE" ]; then
    if [ ! -f "$DEFAULT_FILE" ]; then
        echo "ERROR: нет ни $ENV_FILE, ни шаблона $DEFAULT_FILE." >&2
        exit 1
    fi
    cp "$DEFAULT_FILE" "$ENV_FILE"
    echo "Создан $ENV_FILE из $DEFAULT_FILE."
fi

[ "$MODE" = "--create-only" ] && exit 0

# Value of a variable: last assignment wins, surrounding spaces and quotes
# are stripped; empty when the variable is absent.
value_of() {
    sed -n "s/^[[:space:]]*$1[[:space:]]*=//p" "$ENV_FILE" \
        | tail -n 1 \
        | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' \
              -e 's/^"\(.*\)"$/\1/' -e "s/^'\(.*\)'$/\1/"
}

if [ -z "$(value_of LOG_DIR)" ]; then
    tmp=$(mktemp)
    if grep -q "^[[:space:]]*LOG_DIR[[:space:]]*=" "$ENV_FILE"; then
        sed "s|^[[:space:]]*LOG_DIR[[:space:]]*=.*|LOG_DIR=$DEFAULT_LOG_DIR|" \
            "$ENV_FILE" > "$tmp"
    else
        cat "$ENV_FILE" > "$tmp"
        # keep the file ending with a newline before appending
        [ -n "$(tail -c 1 "$ENV_FILE")" ] && echo >> "$tmp"
        echo "LOG_DIR=$DEFAULT_LOG_DIR" >> "$tmp"
    fi
    cat "$tmp" > "$ENV_FILE"
    rm -f "$tmp"
    echo "LOG_DIR не задан: прописан LOG_DIR=$DEFAULT_LOG_DIR в $ENV_FILE."
fi

missing=""
for name in $REQUIRED; do
    [ -z "$(value_of "$name")" ] && missing="$missing $name"
done

if [ -n "$missing" ]; then
    cat >&2 <<EOF
ERROR: в $ENV_FILE не заполнены переменные:
$(for name in $missing; do echo "  - $name"; done)

Откройте $ENV_FILE и задайте значения, например:
  POSTGRES_USER=db_user
  POSTGRES_PASSWORD=<придумайте пароль>
  POSTGRES_DB=webapp
  POSTGRES_HOST=localhost
  POSTGRES_PORT=5432
  SECRET_KEY=<случайная строка, например: openssl rand -hex 32>

POSTGRES_HOST и POSTGRES_PORT нужны для запуска без Docker:
в контейнере app они заменяются на postgres:5432.
Пользователь, пароль и база Postgres создаются при первом запуске
с пустой папкой docker/runtime/postgres. Если вы меняете их позже,
удалите эту папку (данные базы пропадут) или поменяйте их в самой базе.
EOF
    exit 1
fi
