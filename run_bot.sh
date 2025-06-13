#!/bin/bash

# Bot directory
BOT_DIR="/var/www/bots/Tg-Taker-bot-Fn20"
# Python virtual environment path
VENV_PATH="$BOT_DIR/venv/bin/python"
# Main script path
SCRIPT_PATH="$BOT_DIR/main.py"

# Activate virtual environment and run the bot
cd $BOT_DIR
$VENV_PATH $SCRIPT_PATH >> $BOT_DIR/bot.log 2>&1 