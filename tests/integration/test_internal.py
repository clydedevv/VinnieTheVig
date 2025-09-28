#!/usr/bin/env python3
"""
Internal Testing Script for AIGG Market Matching & URL Generation
"""

import sys
import os
sys.path.append('src')
sys.path.append('.')

from src.flows.dspy_enhanced_aigg_flow import DSPyEnhancedAIGGFlow
import requests

def test_market_matching():
    """Test market matching for common queries"""
    
    print("🧪 AIGG INTERNAL TESTING - Market Matching & URL Generation")
    print("=" * 70)
    
    # Initialize the flow
    try:
        flow = DSPyEnhancedAIGGFlow()
        print("✅ DSPy Enhanced AIGG Flow initialized")
    except Exception as e:
        print(f"❌ Failed to initialize flow: {e}")
        return
    
    # Test queries
    test_queries = [
        "Will Bitcoin hit $150K this year?",
        "Iran nuke in 2025?", 
        "Trump election odds?",
        "Will Bitcoin reach $150K by January 31, 2025?"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing Query: '{query}'")
        print("-" * 50)
        
        try:
            # This should call the flow's main method
            result = flow.forward(query=query)
            
            print(f"✅ Analysis completed")
            print(f"📊 Result length: {len(str(result))} characters")
            print(f"📝 First 200 chars: {str(result)[:200]}...")
            
            # Extract any URLs from the result
            result_str = str(result)
            if "polymarket.com" in result_str:
                url_start = result_str.find("https://polymarket.com")
                url_end = result_str.find(" ", url_start) if result_str.find(" ", url_start) > 0 else len(result_str)
                url = result_str[url_start:url_end]
                print(f"🔗 Generated URL: {url}")
                
                # Test if URL is accessible
                try:
                    response = requests.head(url, timeout=5)
                    if response.status_code == 200:
                        print(f"✅ URL is accessible (200)")
                    else:
                        print(f"❌ URL returns {response.status_code}")
                except Exception as e:
                    print(f"❌ URL test failed: {e}")
            
        except Exception as e:
            print(f"❌ Query failed: {e}")
    
    print("\n" + "=" * 70)
    print("🎯 TESTING COMPLETE")

def test_specific_markets():
    """Test specific markets we know exist"""
    
    print("\n🎯 TESTING SPECIFIC KNOWN MARKETS")
    print("=" * 70)
    
    # Test known market slugs
    known_markets = [
        "iran-nuke-in-2025",
        "will-bitcoin-reach-150000-by-january-31-2025", 
        "will-bitcoin-reach-150000-in-november"
    ]
    
    for slug in known_markets:
        url = f"https://polymarket.com/event/{slug}"
        print(f"\n🔗 Testing: {url}")
        
        try:
            response = requests.head(url, timeout=5)
            print(f"   Status: {response.status_code}")
            if response.status_code != 200:
                print(f"   ❌ Market URL may be incorrect")
            else:
                print(f"   ✅ Market URL is accessible")
        except Exception as e:
            print(f"   ❌ Connection failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting AIGG Internal Testing...")
    test_market_matching()
    test_specific_markets()
    print("\n✅ Internal testing complete!") 