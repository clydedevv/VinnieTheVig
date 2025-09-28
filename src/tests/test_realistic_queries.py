#!/usr/bin/env python3
"""
Test realistic user queries against actual markets to improve matching
"""
import requests
import json

API_BASE = "http://localhost:8001"

def test_realistic_queries():
    """Test queries that real users would ask"""
    
    # Realistic queries based on actual markets in our database
    test_cases = [
        {
            "query": "Will Elon cut government spending in 2025?",
            "expected": "Should match Elon DOGE budget cutting markets"
        },
        {
            "query": "XRP strategic reserve crypto policy",
            "expected": "Should match US national XRP reserve market"
        },
        {
            "query": "Trump cabinet appointments 2025",
            "expected": "Should match Trump-related political markets"
        },
        {
            "query": "Federal budget cuts government efficiency",
            "expected": "Should match federal spending decrease markets"
        },
        {
            "query": "NBA finals winner this year",
            "expected": "Should match 2025 NBA championship markets"
        },
        {
            "query": "Bitcoin price predictions end of year",
            "expected": "Should match Bitcoin price target markets"
        },
        {
            "query": "Russia Ukraine conflict resolution",
            "expected": "Should match Russia/Ukraine ceasefire markets"
        },
        {
            "query": "AI breakthrough artificial intelligence GPT",
            "expected": "Should match AI/tech advancement markets"
        }
    ]
    
    print("🎯 REALISTIC QUERY TESTING")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        query = test_case["query"]
        expected = test_case["expected"]
        
        print(f"\n🔍 Test {i}: '{query}'")
        print(f"Expected: {expected}")
        print("-" * 50)
        
        try:
            response = requests.get(
                f"{API_BASE}/markets/search",
                params={"q": query, "limit": 3, "min_relevance": 0.5},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                markets = data.get('markets', [])
                
                if markets:
                    print(f"✅ Found {len(markets)} relevant markets:")
                    for j, market in enumerate(markets, 1):
                        score = market.get('relevance_score', 0)
                        title = market.get('title', '')
                        end_date = market.get('end_date', '')[:10]  # Just date part
                        print(f"   {j}. Score {score:.3f}: {title}")
                        print(f"      End: {end_date}")
                else:
                    print("❌ No relevant markets found (score < 0.5)")
                    
                    # Try with lower threshold
                    response2 = requests.get(
                        f"{API_BASE}/markets/search",
                        params={"q": query, "limit": 3, "min_relevance": 0.1},
                        timeout=10
                    )
                    
                    if response2.status_code == 200:
                        data2 = response2.json()
                        markets2 = data2.get('markets', [])
                        if markets2:
                            print(f"⚠️  With lower threshold (0.1+), found {len(markets2)} markets:")
                            for j, market in enumerate(markets2, 1):
                                score = market.get('relevance_score', 0)
                                title = market.get('title', '')[:60]
                                print(f"   {j}. Score {score:.3f}: {title}...")
            else:
                print(f"❌ API Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
    
    print(f"\n🎯 Analysis: Identify which queries need better matching")

if __name__ == "__main__":
    test_realistic_queries() 