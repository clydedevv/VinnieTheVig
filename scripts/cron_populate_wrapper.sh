#!/bin/bash
# Cron wrapper for populate_polymarket_data_clob.py
# Ensures proper environment and logging

# Set up environment
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
export HOME="/home/cosmos"
cd /home/cosmos/aigg-insights

# Load environment variables
source .env

# Activate virtual environment
source venv/bin/activate

# Run the populate script with proper logging
echo "$(date): Starting Polymarket data population..." >> logs/polymarket_cron.log
python scripts/populate_polymarket_data_clob.py >> logs/polymarket_cron.log 2>&1
echo "$(date): Polymarket data population completed with exit code $?" >> logs/polymarket_cron.log
echo "---" >> logs/polymarket_cron.log

