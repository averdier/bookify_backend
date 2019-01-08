#!/bin/bash

set -e
echo "Creating database"
python create_database.py
echo "Database created"

exec "$@"