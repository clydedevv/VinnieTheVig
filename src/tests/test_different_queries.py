#!/usr/bin/env python3
"""
Test different queries to see market matching capabilities
"""
from simple_flow import AIGGFlow

def test_multiple_queries():
    """Test various queries to see what markets we can find"""
    
    flow = AIGGFlow()
    
    test_queries = [
        "Trump election 2024",
        "Bitcoin price",
        "AI stocks",
        "Federal Reserve interest rates",
        "Climate change",
        "Tesla stock price",
        "World Cup 2024",
        "COVID pandemic",
        "Recession 2024"
    ]
    
    print("🧪 Testing Multiple Queries")
    print("=" * 50)
    
    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        print("-" * 30)
        
        try:
            # Just test market finding, not full analysis
            markets = flow.polymarket.fetch_markets(limit=100)
            relevant_market = flow.polymarket.find_relevant_market(query, markets)
            
            if relevant_market:
                print(f"✅ Found: {relevant_market.question}")
                print(f"💰 Volume: ${relevant_market.volume_24h:,.0f}")
                print(f"🆔 ID: {relevant_market.id[:20]}...")
            else:
                print("❌ No relevant market found")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_multiple_queries() 