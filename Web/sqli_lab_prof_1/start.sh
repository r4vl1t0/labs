#!/bin/sh

if [ ! -f database.db ]; then
    python init_db.py
fi

python app.py
