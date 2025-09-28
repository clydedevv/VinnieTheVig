#!/bin/bash

# AIGG System Status Check Script

echo "📊 AIGG Infrastructure Status Check"
echo "=================================="

# Check tmux sessions
echo ""
echo "🔄 TMux Sessions:"
tmux list-sessions 2>/dev/null | grep -E "(aigg-api|twitter-wrapper|aigg-twitter-bot)" || echo "   No AIGG tmux sessions running"

# Check API endpoints
echo ""
echo "🌐 API Health Checks:"

# Main API (port 8001)
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/health 2>/dev/null | grep -q "200"; then
    echo "   ✅ Main API (8001): Online"
else
    echo "   ❌ Main API (8001): Offline"
fi

# Twitter Wrapper API (port 8003)
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8003/health 2>/dev/null | grep -q "200"; then
    echo "   ✅ Wrapper API (8003): Online"
else
    echo "   ❌ Wrapper API (8003): Offline"
fi

# Check database connection
echo ""
echo "🗄️  Database Connection:"
cd /home/cosmos/aigg-insights
if source venv/bin/activate && python -c "import psycopg2; conn = psycopg2.connect(host='localhost', database='aigg_insights', user='aigg_user', password='aigg2024'); conn.close(); print('   ✅ PostgreSQL: Connected')" 2>/dev/null; then
    :
else
    echo "   ❌ PostgreSQL: Connection failed"
fi

# Check disk space
echo ""
echo "💾 Disk Space:"
df -h / | awk 'NR==2{printf "   📁 Root: %s used (%s available)\n", $5, $4}'

# Check virtual environment
echo ""
echo "🐍 Python Environment:"
if [ -d "venv" ]; then
    echo "   ✅ Virtual environment: Present"
else
    echo "   ❌ Virtual environment: Missing"
fi

# Check .env file
if [ -f ".env" ]; then
    echo "   ✅ Environment file: Present"
else
    echo "   ❌ Environment file: Missing"
fi

# Check cron jobs
echo ""
echo "⏰ Scheduled Tasks:"
cron_count=$(crontab -l 2>/dev/null | grep -c "aigg-insights" || echo "0")
echo "   📅 AIGG cron jobs: $cron_count configured"

echo ""
echo "✅ Status check complete!" 