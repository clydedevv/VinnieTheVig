#!/bin/bash

# AIGG Insights Streamlit Test Interface Launcher

echo "🎯 Starting AIGG Insights Test Interface..."
echo ""

# Parse command line arguments
USE_PRODUCTION=false
if [[ "$1" == "--production" ]] || [[ "$1" == "-p" ]]; then
    USE_PRODUCTION=true
fi

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "❌ Streamlit not found. Installing dependencies..."
    pip install streamlit
fi

if [ "$USE_PRODUCTION" = true ]; then
    echo "📡 Using PRODUCTION server at 65.108.231.245"
    echo ""
    
    # Test production API connection
    echo "🔍 Testing connection to production API..."
    if curl -s http://65.108.231.245:8001/health > /dev/null; then
        echo "✅ Production API is accessible"
    else
        echo "⚠️  Warning: Could not reach production API at http://65.108.231.245:8001"
        echo "The server might be down or there might be a network issue"
    fi
    
    # Launch with production flag
    echo "🚀 Launching Streamlit interface (Production mode)..."
    USE_PRODUCTION_API=true streamlit run tools/streamlit_test_app.py --server.port 8502
else
    echo "💻 Using LOCAL server at localhost:8001"
    echo "   To use production server, run: ./run_streamlit.sh --production"
    echo ""
    
    # Check if Market API is running locally
    if ! curl -s http://localhost:8001/health > /dev/null; then
        echo "⚠️  Warning: Market API not running on port 8001"
        echo "To start it, run: python main.py api-server --port 8001"
        echo ""
    fi
    
    # Launch in local mode
    echo "🚀 Launching Streamlit interface (Local mode)..."
    streamlit run tools/streamlit_test_app.py --server.port 8502
fi