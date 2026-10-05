#!/usr/bin/env bash
set -e

# The official PostgreSQL image runs this only when its data volume is empty.
# Credentials come from the container environment, never from this file.
: "${ODOO_DB_PASSWORD:?ODOO_DB_PASSWORD must be set}"

psql --username="$POSTGRES_USER" --dbname="$POSTGRES_DB" \
    --set=ON_ERROR_STOP=1 --set=odoo_db_password="$ODOO_DB_PASSWORD" <<'SQL'
CREATE ROLE odoo WITH LOGIN NOSUPERUSER NOCREATEROLE CREATEDB
    PASSWORD :'odoo_db_password';
SQL
