#!/usr/bin/env python3
"""
AIGG External Client - Developer Testing Interface
For external developers to test and improve AIGG flow without server access

Usage:
    python external_client.py analyze "your query here"
    python external_client.py test-api [--host HOST]
    python external_client.py batch-test [--file FILE]
    python external_client.py twitter-format "your query"
    python external_client.py market-search "your query"
    python external_client.py --help

Examples:
    python external_client.py analyze "Will Bitcoin reach $200k in 2025?"
    python external_client.py test-api --host 37.27.54.184
    python external_client.py twitter-format "US Iran nuclear deal?"
    python external_client.py market-search "bitcoin price prediction"
"""

import sys
import os
import argparse
import requests
import json
import time
from typing import List, Dict, Any, Optional

# Add src to path for local imports (if running locally)
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

class AIGGExternalClient:
    """External client for testing AIGG functionality"""
    
    def __init__(self, api_host: str = "37.27.54.184", api_port: int = 8001, wrapper_port: int = 8003):
        self.api_host = api_host
        self.api_port = api_port
        self.wrapper_port = wrapper_port
        self.api_base = f"http://{api_host}:{api_port}"
        self.wrapper_base = f"http://{api_host}:{wrapper_port}"
        
    def test_api_connection(self) -> bool:
        """Test if APIs are accessible"""
        print("🔍 Testing API connections...")
        
        # Test main API
        try:
            response = requests.get(f"{self.api_base}/health", timeout=10)
            if response.status_code == 200:
                print(f"✅ Main API ({self.api_host}:{self.api_port}): Online")
                main_api_ok = True
            else:
                print(f"⚠️  Main API ({self.api_host}:{self.api_port}): Issues detected")
                main_api_ok = False
        except Exception as e:
            print(f"❌ Main API ({self.api_host}:{self.api_port}): Offline - {e}")
            main_api_ok = False
        
        # Test wrapper API
        try:
            response = requests.get(f"{self.wrapper_base}/health", timeout=10)
            if response.status_code == 200:
                print(f"✅ Wrapper API ({self.api_host}:{self.wrapper_port}): Online")
                wrapper_api_ok = True
            else:
                print(f"⚠️  Wrapper API ({self.api_host}:{self.wrapper_port}): Issues detected")
                wrapper_api_ok = False
        except Exception as e:
            print(f"❌ Wrapper API ({self.api_host}:{self.wrapper_port}): Offline - {e}")
            wrapper_api_ok = False
        
        return main_api_ok and wrapper_api_ok
    
    def search_markets(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for relevant markets"""
        print(f"🔍 Searching markets for: '{query}'")
        
        try:
            response = requests.get(
                f"{self.api_base}/markets/search",
                params={"q": query, "limit": limit},
                timeout=15
            )
            response.raise_for_status()
            
            data = response.json()
            markets = data.get("markets", [])
            
            print(f"📊 Found {len(markets)} markets:")
            for i, market in enumerate(markets[:5], 1):
                print(f"   {i}. {market.get('title', 'Unknown')[:70]}...")
                print(f"      Category: {market.get('category', 'Unknown')}")
                print(f"      Active: {market.get('active', 'Unknown')}")
                print()
            
            return markets
            
        except Exception as e:
            print(f"❌ Market search failed: {e}")
            return []
    
    def analyze_query(self, query: str) -> Optional[Dict[str, Any]]:
        """Run full AIGG analysis via wrapper API"""
        print(f"🚀 Running AIGG analysis for: '{query}'")
        print("=" * 60)
        
        try:
            start_time = time.time()
            
            payload = {
                "query": query,
                "user_id": "external_client",
                "user_handle": "external_test",
                "tweet_id": "test_tweet"
            }
            
            response = requests.post(
                f"{self.wrapper_base}/analyze",
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            processing_time = time.time() - start_time
            
            if result.get("success"):
                print("✅ Analysis completed successfully!")
                print(f"⏱️  Processing time: {processing_time:.2f}s")
                print()
                print("📊 Results:")
                print(f"Market: {result.get('market_title', 'Unknown')}")
                print(f"Analysis: {result.get('analysis', 'No analysis')}")
                print(f"Recommendation: {result.get('recommendation', 'No recommendation')}")
                print(f"Confidence: {result.get('confidence', 0):.0%}")
                print(f"URL: {result.get('polymarket_url', 'No URL')}")
                print()
                print("🐦 Twitter Response:")
                print("-" * 40)
                print(result.get('tweet_text', 'No tweet text'))
                print("-" * 40)
                print(f"Length: {len(result.get('tweet_text', ''))} characters")
                
                return result
            else:
                print(f"❌ Analysis failed: {result.get('error_message', 'Unknown error')}")
                return None
                
        except Exception as e:
            print(f"❌ Analysis error: {e}")
            return None
    
    def test_twitter_formatting(self, query: str) -> None:
        """Test Twitter response formatting"""
        print(f"🐦 Testing Twitter formatting for: '{query}'")
        
        result = self.analyze_query(query)
        if result and result.get("success"):
            tweet_text = result.get("tweet_text", "")
            
            print(f"\n📝 Format Analysis:")
            print(f"Character count: {len(tweet_text)}/280")
            print(f"Under limit: {'✅' if len(tweet_text) <= 280 else '❌'}")
            
            lines = tweet_text.split('\n')
            print(f"Line count: {len(lines)}")
            for i, line in enumerate(lines, 1):
                print(f"  Line {i}: {len(line)} chars - {line}")
    
    def batch_test(self, queries: List[str]) -> None:
        """Run batch testing on multiple queries"""
        print(f"🧪 Running batch test on {len(queries)} queries...")
        print("=" * 60)
        
        results = []
        for i, query in enumerate(queries, 1):
            print(f"\n[{i}/{len(queries)}] Testing: {query}")
            print("-" * 40)
            
            start_time = time.time()
            result = self.analyze_query(query)
            processing_time = time.time() - start_time
            
            results.append({
                "query": query,
                "success": result is not None and result.get("success", False),
                "processing_time": processing_time,
                "result": result
            })
            
            # Small delay between requests
            time.sleep(1)
        
        # Summary
        print("\n📊 Batch Test Summary:")
        print("=" * 40)
        successful = sum(1 for r in results if r["success"])
        avg_time = sum(r["processing_time"] for r in results) / len(results)
        
        print(f"Success rate: {successful}/{len(results)} ({successful/len(results)*100:.1f}%)")
        print(f"Average processing time: {avg_time:.2f}s")
        
        for result in results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['query'][:50]}... ({result['processing_time']:.1f}s)")

def load_test_queries(filename: str = "test_queries.txt") -> List[str]:
    """Load test queries from file"""
    try:
        with open(filename, 'r') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        print(f"⚠️  Test file {filename} not found. Creating sample file...")
        sample_queries = [
            "Will Bitcoin reach $200k in 2025?",
            "Who will win the 2024 election?",
            "Will there be a US-Iran nuclear deal in 2025?",
            "Will Tesla stock hit $500 this year?",
            "Will AI achieve AGI by 2030?",
            "Will Trump be elected president in 2024?",
            "Will Bitcoin ETF get approved?",
            "Will Lakers win NBA championship?",
            "Will inflation drop below 2% in 2025?",
            "Will there be a recession in 2025?"
        ]
        
        with open(filename, 'w') as f:
            f.write("# AIGG Test Queries\n")
            f.write("# Add your test queries here, one per line\n")
            f.write("# Lines starting with # are ignored\n\n")
            for query in sample_queries:
                f.write(f"{query}\n")
        
        print(f"📝 Created sample file: {filename}")
        return sample_queries

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="AIGG External Client - Developer Testing Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Run AIGG analysis on a query')
    analyze_parser.add_argument('query', help='Query to analyze')
    analyze_parser.add_argument('--host', default="37.27.54.184", help='API host')
    
    # Test API command
    test_parser = subparsers.add_parser('test-api', help='Test API connections')
    test_parser.add_argument('--host', default="37.27.54.184", help='API host')
    
    # Twitter format test
    twitter_parser = subparsers.add_parser('twitter-format', help='Test Twitter formatting')
    twitter_parser.add_argument('query', help='Query to test')
    twitter_parser.add_argument('--host', default="37.27.54.184", help='API host')
    
    # Market search
    search_parser = subparsers.add_parser('market-search', help='Search for markets')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--limit', type=int, default=10, help='Number of results')
    search_parser.add_argument('--host', default="37.27.54.184", help='API host')
    
    # Batch test
    batch_parser = subparsers.add_parser('batch-test', help='Run batch tests')
    batch_parser.add_argument('--file', default="test_queries.txt", help='File with test queries')
    batch_parser.add_argument('--host', default="37.27.54.184", help='API host')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    print("🧪 AIGG External Client - Developer Testing Interface")
    print("=" * 60)
    
    # Initialize client
    client = AIGGExternalClient(api_host=getattr(args, 'host', '37.27.54.184'))
    
    if args.command == 'analyze':
        client.analyze_query(args.query)
    elif args.command == 'test-api':
        client.test_api_connection()
    elif args.command == 'twitter-format':
        client.test_twitter_formatting(args.query)
    elif args.command == 'market-search':
        client.search_markets(args.query, args.limit)
    elif args.command == 'batch-test':
        queries = load_test_queries(args.file)
        client.batch_test(queries)

if __name__ == "__main__":
    main() 