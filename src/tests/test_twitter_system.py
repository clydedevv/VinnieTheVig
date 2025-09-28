#!/usr/bin/env python3
"""
Test script for AIGG Twitter integration components
"""

import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

def test_query_extraction():
    """Test the query extraction functionality"""
    print("🔍 Testing query extraction...")
    
    try:
        from src.twitter.client import TwitterClient
        
        # Create client without authentication for testing
        client = TwitterClient.__new__(TwitterClient)
        client.bot_handle = "@aigg_bot"
        
        test_tweets = [
            "Will Bitcoin reach $150k this year?",
            "@aigg_bot what are the odds of Trump winning the election?",
            "Should I bet on the Lakers to win the NBA championship?",
            "Just had lunch with friends",  # Should not be detected
            "When will the Fed raise interest rates next?",
            "@aigg_bot prediction for crypto market in 2025?",
            "hello world",  # Should not be detected
            "Who will win the next presidential election?",
        ]
        
        for tweet in test_tweets:
            query = client.extract_prediction_query(tweet)
            if query:
                print(f"✅ '{tweet}' -> '{query.extracted_query}' (confidence: {query.confidence:.2f})")
            else:
                print(f"❌ '{tweet}' -> No query detected")
        
        return True
        
    except Exception as e:
        print(f"❌ Query extraction test failed: {e}")
        return False

def test_twitter_formatting():
    """Test Twitter response formatting"""
    print("\n📱 Testing Twitter response formatting...")
    
    try:
        from src.api_wrapper.twitter_wrapper import format_for_twitter
        from dataclasses import dataclass
        
        # Mock analysis result
        @dataclass
        class MockResult:
            analysis: str
            recommendation: str
            confidence: float
            polymarket_url: str
        
        # Test different length scenarios
        test_cases = [
            {
                "query": "Will Bitcoin reach $150k?",
                "result": MockResult(
                    analysis="Bitcoin is currently trading at $95k with strong institutional demand but faces resistance at $100k level.",
                    recommendation="BUY",
                    confidence=0.75,
                    polymarket_url="https://polymarket.com/event/will-bitcoin-reach-150k-in-june"
                )
            },
            {
                "query": "Very long question about whether the Federal Reserve will raise interest rates in the next meeting considering inflation data and employment statistics?",
                "result": MockResult(
                    analysis="Federal Reserve policy depends on multiple economic indicators including inflation rates, employment data, GDP growth, and global economic conditions. Recent data suggests mixed signals with inflation cooling but employment remaining strong.",
                    recommendation="HOLD",
                    confidence=0.60,
                    polymarket_url="https://polymarket.com/event/fed-rate-decision-march-2025"
                )
            }
        ]
        
        for case in test_cases:
            tweet_text = format_for_twitter(case["result"], case["query"])
            print(f"\n📝 Query: {case['query']}")
            print(f"📱 Tweet ({len(tweet_text)} chars):")
            print(f"   {tweet_text}")
            
            if len(tweet_text) > 280:
                print(f"⚠️  Tweet too long: {len(tweet_text)} characters")
            else:
                print(f"✅ Tweet fits: {len(tweet_text)}/280 characters")
        
        return True
        
    except Exception as e:
        print(f"❌ Twitter formatting test failed: {e}")
        return False

def test_aigg_integration():
    """Test integration with AIGG flow"""
    print("\n🤖 Testing AIGG integration...")
    
    try:
        from src.flows.dspy_enhanced_aigg_flow import DSPyEnhancedAIGGFlow
        
        flow = DSPyEnhancedAIGGFlow()
        
        # Test a simple query
        result = flow.analyze_query("Will Bitcoin reach $150k this year?")
        
        if result:
            print("✅ AIGG flow working:")
            print(f"   Market: {result.selected_market.title}")
            print(f"   Analysis: {result.analysis[:100]}...")
            print(f"   Recommendation: {result.recommendation} ({result.confidence:.0%})")
            print(f"   URL: {result.polymarket_url}")
            return True
        else:
            print("❌ No result from AIGG flow")
            return False
            
    except Exception as e:
        print(f"❌ AIGG integration test failed: {e}")
        return False

def test_wrapper_api_offline():
    """Test wrapper API components without running server"""
    print("\n🔗 Testing wrapper API components...")
    
    try:
        from src.api_wrapper.twitter_wrapper import format_for_twitter, TwitterAnalysisRequest
        
        # Test request model
        request = TwitterAnalysisRequest(
            query="Will Bitcoin reach $150k?",
            user_id="test_user_123",
            user_handle="test_user"
        )
        
        print(f"✅ Request model: {request.query} from @{request.user_handle}")
        
        return True
        
    except Exception as e:
        print(f"❌ Wrapper API test failed: {e}")
        return False

def test_image_enrichment_offline():
    """Simulate an image tweet by passing a local file as data URL and a remote-like media URL."""
    print("\n🖼️  Testing image enrichment logic (offline simulation)...")
    try:
        import base64
        img_path = "/home/cosmos/aigg-insights/tests/live_tests/multimedia1.png"
        image_urls = []
        # Prefer real URL path in production; for test, pack as data URL so Fireworks can read it as inline
        if os.path.exists(img_path):
            with open(img_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")
            data_url = f"data:image/png;base64,{b64}"
            image_urls.append(data_url)
        else:
            print(f"⚠️  Local test image not found: {img_path}. Skipping inline test.")
        
        from src.api_wrapper.twitter_wrapper import analyze_for_twitter, TwitterAnalysisRequest
        import asyncio
        
        req = TwitterAnalysisRequest(
            query="What does this image show about the market?",
            user_id="test_user_vision",
            user_handle="tester",
            media_urls=image_urls
        )
        # Run the FastAPI handler directly
        resp = asyncio.get_event_loop().run_until_complete(analyze_for_twitter(req))
        assert resp and getattr(resp, 'tweet_text', None)
        print(f"✅ Image enrichment tweet length: {len(resp.tweet_text)}")
        return True
    except Exception as e:
        print(f"❌ Image enrichment test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🐦 AIGG Twitter System Tests")
    print("=" * 50)
    
    tests = [
        test_query_extraction,
        test_twitter_formatting,
        test_aigg_integration,
        test_wrapper_api_offline,
        test_image_enrichment_offline
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"🏆 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🚀 All systems ready for Twitter integration!")
        print("\n📋 Next steps:")
        print("   1. Set up Twitter API credentials")
        print("   2. Start wrapper API on port 8002")
        print("   3. Run Twitter bot monitoring")
    else:
        print("❌ Some tests failed - fix issues before deployment")

if __name__ == "__main__":
    main() 