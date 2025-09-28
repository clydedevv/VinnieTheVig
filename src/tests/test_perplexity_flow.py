#!/usr/bin/env python3
"""
Test the enhanced AIGG flow with Perplexity integration
"""
from simple_flow import AIGGFlow

def test_enhanced_flow():
    """Test multiple queries with the enhanced Perplexity-powered flow"""
    
    flow = AIGGFlow()
    
    test_queries = [
        "Bitcoin price will hit $150k in 2024",
        "Federal Reserve will cut interest rates",
        "AI will achieve AGI by 2025"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*70}")
        print(f"🧪 TEST {i}: {query}")
        print('='*70)
        
        try:
            result = flow.run_analysis(query)
            if result:
                print(f"\n📋 DETAILED RESULT:")
                print(f"🎯 Market Found: {result.market.question[:80]}...")
                print(f"💰 Market Volume: ${result.market.volume_24h:,.0f}")
                print(f"🔍 Research Sources: {', '.join(result.research.sources)}")
                print(f"📊 Key Research Points:")
                for point in result.research.key_points[:3]:
                    print(f"   • {point}")
                print(f"🤖 AI Recommendation: {result.recommendation.upper()}")
                print(f"💸 Suggested Bet Size: {result.bet_size}")
                print(f"📈 Confidence Level: {result.confidence:.1%}")
                print(f"🧠 AI Reasoning: {result.reasoning}")
            else:
                print("❌ No result generated")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        if i < len(test_queries):
            print(f"\n⏳ Waiting before next test...")
            import time
            time.sleep(2)  # Brief pause between tests

if __name__ == "__main__":
    print("🚀 Testing Enhanced AIGG Flow with Perplexity")
    print("This will test web search + reasoning + recommendations")
    test_enhanced_flow()
    print(f"\n✨ Testing complete! The enhanced flow uses:")
    print("  🌐 Perplexity Sonar for web research")
    print("  🧠 Perplexity R1-1776 for reasoning & analysis")
    print("  🎯 AI-powered betting recommendations") 