#!/usr/bin/env python3
"""
AIGG Insights - Main Entry Point
Production-ready AI-powered prediction market analysis system

Usage:
    python main.py twitter-bot [--interval SECONDS] [--disable-whitelist]
    python main.py api-server [--port PORT] [--host HOST]
    python main.py wrapper-api [--port PORT]
    python main.py analyze "query"
    python main.py test [--component COMPONENT]
    python main.py status
    python main.py --help

Commands:
    twitter-bot     Start the Twitter bot service
    api-server      Start the main AIGG API server
    wrapper-api     Start the Twitter wrapper API
    analyze         Run a single analysis query
    test            Run system tests
    status          Check system status
"""

import sys
import os
import argparse
import subprocess
import time
from typing import Optional

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def start_twitter_bot(check_interval: int = 30, disable_whitelist: bool = False):  # X Premium: 30 seconds
    """Start the Twitter bot service"""
    print("🤖 Starting AIGG Twitter Bot...")
    
    try:
        from src.twitter.bot import AIGGTwitterBot
        
        # Set environment variables
        if disable_whitelist:
            os.environ['WHITELIST_ENABLED'] = 'false'
            print("⚠️  Whitelist disabled - public access enabled")
        
        # Initialize and run bot
        bot = AIGGTwitterBot()
        
        print(f"✅ Twitter Bot initialized")
        print(f"⏱️  Check interval: {check_interval} seconds")
        print(f"🔐 Whitelist enabled: {not disable_whitelist}")
        print("🚀 Bot is now monitoring mentions...")
        
        bot.run_monitoring_loop(check_interval=check_interval)
        
    except KeyboardInterrupt:
        print("\n👋 Twitter bot stopped by user")
    except Exception as e:
        print(f"❌ Twitter bot error: {e}")
        sys.exit(1)

def start_api_server(port: int = 8001, host: str = "0.0.0.0"):
    """Start the main AIGG API server"""
    print(f"🌐 Starting AIGG API Server on {host}:{port}...")
    
    try:
        import uvicorn
        uvicorn.run(
            "api.main:app",
            host=host,
            port=port,
            reload=False,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ API server error: {e}")
        sys.exit(1)

def start_wrapper_api(port: int = 8003):
    """Start the Twitter wrapper API"""
    print(f"🔗 Starting Twitter Wrapper API on port {port}...")
    
    try:
        import uvicorn
        uvicorn.run(
            "src.api_wrapper.twitter_wrapper:app",
            host="0.0.0.0",
            port=port,
            reload=False,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Wrapper API error: {e}")
        sys.exit(1)

def run_analysis(query: str):
    """Run a single analysis query"""
    print(f"🔍 Analyzing: '{query}'")
    print("=" * 60)
    
    try:
        from src.flows.dspy_enhanced_aigg_flow import DSPyEnhancedAIGGFlow
        
        aigg_flow = DSPyEnhancedAIGGFlow()
        result = aigg_flow.analyze_query(query)
        
        if result:
            print("✅ Analysis complete!")
            aigg_flow.print_result(result)
        else:
            print("❌ No relevant markets found for your query")
            
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        sys.exit(1)

def run_tests(component: Optional[str] = None):
    """Run system tests"""
    print("🧪 Running AIGG system tests...")
    
    try:
        if component == "twitter":
            from src.tests.test_twitter_system import main as test_twitter
            test_twitter()
        elif component == "api":
            print("Testing API endpoints...")
            subprocess.run(["python", "-m", "pytest", "src/tests/", "-v"], check=True)
        elif component == "flow":
            print("Testing DSPy Enhanced Flow...")
            from src.flows.dspy_enhanced_aigg_flow import DSPyEnhancedAIGGFlow
            flow = DSPyEnhancedAIGGFlow()
            result = flow.analyze_query("Will Bitcoin reach $150k by end of 2025?")
            if result:
                print(f"✅ Flow test passed: {result.recommendation}")
        else:
            print("Running comprehensive tests...")
            subprocess.run(["python", "-m", "pytest", "tests/", "-v"], check=True)
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        sys.exit(1)

def check_status():
    """Check system status"""
    print("📊 AIGG System Status Check")
    print("=" * 40)
    
    # Check API Server
    try:
        import requests
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            print("✅ Main API Server: Online")
        else:
            print("⚠️  Main API Server: Issues detected")
    except:
        print("❌ Main API Server: Offline")
    
    # Check Wrapper API
    try:
        import requests
        response = requests.get("http://localhost:8003/health", timeout=5)
        if response.status_code == 200:
            print("✅ Wrapper API: Online")
        else:
            print("⚠️  Wrapper API: Issues detected")
    except:
        print("❌ Wrapper API: Offline")
    
    # Check database connection
    try:
        from src.flows.dspy_enhanced_aigg_flow import DSPyEnhancedAIGGFlow
        flow = DSPyEnhancedAIGGFlow()
        markets = flow.get_top_markets("test", limit=1)
        if markets:
            print("✅ Database: Connected")
        else:
            print("⚠️  Database: No markets found")
    except:
        print("❌ Database: Connection failed")
    
    # Check TMux sessions
    try:
        result = subprocess.run(["tmux", "list-sessions"], 
                              capture_output=True, text=True)
        if "aigg-bot" in result.stdout:
            print("✅ Twitter Bot: Running in tmux")
        else:
            print("❌ Twitter Bot: Not found in tmux")
            
        if "twitter-wrapper" in result.stdout:
            print("✅ Wrapper API: Running in tmux")
        else:
            print("❌ Wrapper API: Not found in tmux")
    except:
        print("⚠️  TMux: Not available")

def main():
    """Main entry point with argument parsing"""
    parser = argparse.ArgumentParser(
        description="AIGG Insights - AI-powered prediction market analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Twitter bot command
    bot_parser = subparsers.add_parser('twitter-bot', help='Start Twitter bot')
    bot_parser.add_argument('--interval', type=int, default=900, 
                           help='Check interval in seconds (default: 900)')
    bot_parser.add_argument('--disable-whitelist', action='store_true',
                           help='Disable whitelist for public access')
    
    # API server command
    api_parser = subparsers.add_parser('api-server', help='Start main API server')
    api_parser.add_argument('--port', type=int, default=8001, help='Port number')
    api_parser.add_argument('--host', default="0.0.0.0", help='Host address')
    
    # Wrapper API command
    wrapper_parser = subparsers.add_parser('wrapper-api', help='Start wrapper API')
    wrapper_parser.add_argument('--port', type=int, default=8003, help='Port number')
    
    # Analysis command
    analyze_parser = subparsers.add_parser('analyze', help='Run single analysis')
    analyze_parser.add_argument('query', help='Query to analyze')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Run tests')
    test_parser.add_argument('--component', choices=['twitter', 'api', 'flow'],
                            help='Test specific component')
    
    # Status command
    subparsers.add_parser('status', help='Check system status')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    print("🤖 AIGG Insights - AI-Powered Prediction Market Analysis")
    print("=" * 60)
    
    if args.command == 'twitter-bot':
        start_twitter_bot(args.interval, args.disable_whitelist)
    elif args.command == 'api-server':
        start_api_server(args.port, args.host)
    elif args.command == 'wrapper-api':
        start_wrapper_api(args.port)
    elif args.command == 'analyze':
        run_analysis(args.query)
    elif args.command == 'test':
        run_tests(args.component)
    elif args.command == 'status':
        check_status()

if __name__ == "__main__":
    main() 