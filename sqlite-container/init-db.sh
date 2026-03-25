#!/bin/sh

# Ensure the data directory exists
mkdir -p /data

# If the database file doesn't exist, create an empty one
if [ ! -f /data/todo.db ]; then
    echo "Creating initial database..."
    sqlite3 /data/todo.db "VACUUM;"
fi

# Keep the container alive
tail -f /dev/null
