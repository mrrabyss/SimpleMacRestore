#!/bin/bash
if [ -d ".venv" ]; then 
    source .venv/bin/activate
    python3 main.py "$@" 
else
    echo "It seems that you don't have all dependencies installed, please re-run ./setup.sh again!"
    read -p "Re-run setup.sh? (Y/N): " confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || exit 1
    ./setup.sh
    exec "$0" "$@"
fi