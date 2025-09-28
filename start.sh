#!/bin/bash
cd /home/cosmos/aigg-insights
source venv/bin/activate
exec python main.py "$@"
