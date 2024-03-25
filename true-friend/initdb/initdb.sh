#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE "$DJANGO_DB_NAME" OWNER "$POSTGRES_USER";
    CREATE DATABASE "$API_DB_NAME" OWNER "$POSTGRES_USER";
EOSQL