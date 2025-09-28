#!/usr/bin/env python3
"""
End-to-end test of AIGG flow with realistic tweet queries
Tests market matching + enhanced Perplexity research
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.flows.dspy_enhanced_aigg_flow import DSPyEnhancedAIGGFlow
import logging

logging.basicConfig(level=logging.INFO)

def test_realistic_tweets():
    """Test with realistic tweet-style queries"""
    flow = DSPyEnhancedAIGGFlow()
    
    # Realistic tweet queries (2025 style - no hashtags)
    test_queries = [
        # Crypto queries
        ("yo is btc finally hitting 200k or nah", "Casual crypto query"),
        ("bitcoin looking bullish af, 150k incoming?", "Bullish sentiment query"),
        ("eth flippening when? tired of waiting", "Ethereum vs Bitcoin query"),
        
        # Geopolitical queries  
        ("china taiwan situation getting spicy 👀", "Geopolitical tension query"),
        ("russia ukraine peace talks happening or cap?", "War/peace query"),
        ("iran really building nukes this time?", "Nuclear proliferation query"),
        
        # Politics queries
        ("trump winning 2024 ez clap or what", "Political prediction query"),
        ("biden second term looking rough ngl", "Incumbent analysis query"),
        
        # Sports/Entertainment queries
        ("chiefs three-peat incoming book it", "Sports dynasty query"),
        ("taylor swift engaged yet? my gf keeps asking", "Celebrity gossip query"),
        
        # Tech queries
        ("gpt-5 dropping soon? need that 10x improvement", "AI advancement query"),
        ("apple finally making a car or they gave up", "Tech company pivot query"),
        
        # Economic queries
        ("fed cutting rates or jerome powell cappin", "Monetary policy query"),
        ("recession canceled? economy looking decent", "Economic outlook query"),
        
        # Wild cards
        ("aliens revealed in 2025 im calling it", "Speculation query"),
        ("my portfolio needs a 10x what's the play", "Investment advice query")
    ]
    
    print("=" * 80)
    print("END-TO-END AIGG FLOW TEST WITH REALISTIC TWEETS")
    print("=" * 80)
    
    for query, description in test_queries[:3]:  # Test first 3 to save time/API calls
        print(f"\n{'='*80}")
        print(f"🐦 Tweet: \"{query}\"")
        print(f"📝 Type: {description}")
        print(f"{'='*80}")
        
        try:
            result = flow.analyze_query(query)
            
            if result:
                print("\n📊 SELECTED MARKET:")
                print(f"   Title: {result.selected_market.title}")
                print(f"   Category: {result.selected_market.category}")
                print(f"   Market ID: {result.selected_market.market_id}")
                
                print("\n🔬 RESEARCH HIGHLIGHTS:")
                # Extract key parts from research
                research_lines = result.research_summary.split('\n')
                for line in research_lines:
                    if any(keyword in line for keyword in ['CURRENT SITUATION', 'KEY DATA', 'UPCOMING']):
                        print(f"   {line.strip()}")
                
                print("\n💡 ANALYSIS:")
                print(f"   {result.analysis[:200]}...")
                
                print("\n🎯 RECOMMENDATION:")
                print(f"   Position: {result.recommendation}")
                print(f"   Confidence: {result.confidence:.1%}")
                
                print("\n📱 TWEET RESPONSE:")
                print(f"   {result.short_analysis}")
                
            else:
                print("❌ No result generated")
                
        except Exception as e:
            print(f"⚠️ Error processing query: {e}")
        
        print("\n" + "-" * 80)

def test_research_quality():
    """Test the quality of research extraction"""
    flow = DSPyEnhancedAIGGFlow()
    
    # Test topic extraction
    test_markets = [
        ("Will Bitcoin reach $200,000 by end of 2025?", "Crypto"),
        ("Will China invade Taiwan before 2026?", "Geopolitics"),
        ("Will Taylor Swift and Travis Kelce get engaged in 2025?", "Entertainment"),
        ("Will the Federal Reserve cut interest rates in March 2025?", "Economics")
    ]
    
    print("\n" + "=" * 80)
    print("TESTING RESEARCH TOPIC EXTRACTION")
    print("=" * 80)
    
    for market_title, category in test_markets:
        print(f"\n📊 Market: {market_title}")
        
        try:
            # Test topic extraction directly
            topic_result = flow.topic_extractor(market_question=market_title)
            print(f"   🎯 Research Topic: {topic_result.research_topic}")
            print(f"   🔍 Key Aspects: {topic_result.key_aspects}")
            
        except Exception as e:
            print(f"   ⚠️ Error: {e}")

if __name__ == "__main__":
    # print("Testing realistic tweet queries...")
    # test_realistic_tweets()
    
    print("Testing research topic extraction...")
    test_research_quality()