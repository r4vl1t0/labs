#!/bin/sh
set -e

python app.py &
APP_PID=$!

python bot.py &
BOT_PID=$!

wait $APP_PID $BOT_PID
