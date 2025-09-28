#!/usr/bin/env python3
"""
Test LLM-Based Market Matching
Compares the old hardcoded approach with the new LLM-based approach
"""
import os
import sys
# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.flows.llm_market_matcher import LLMMarketMatcher, MarketData
from .test_market_matching_standalone import calculate_market_relevance


def get_test_markets():
    """Get test markets based on real Polymarket data"""
    return [
        MarketData(
            id="btc-200k-eoy",
            title="Will Bitcoin reach $200,000 by end of 2025?",
            category="Crypto",
            end_date="2025-12-31T23:59:59Z",
            active=True
        ),
        MarketData(
            id="btc-150k-june",
            title="Will Bitcoin hit $150,000 by June 2025?",
            category="Crypto",
            end_date="2025-06-30T23:59:59Z",
            active=True
        ),
        MarketData(
            id="btc-120k-2025",
            title="Will Bitcoin hit $120,000 in 2025?",
            category="Crypto",
            end_date="2025-12-31T23:59:59Z",
            active=True
        ),
        MarketData(
            id="fed-cuts-2025",
            title="How many times will the Fed cut rates in 2025?",
            category="Economics",
            end_date="2025-12-31T23:59:59Z",
            active=True
        ),
        MarketData(
            id="fed-march-cut",
            title="Will the Fed cut rates at the March 2025 FOMC meeting?",
            category="Economics",
            end_date="2025-03-19T18:00:00Z",
            active=True
        ),
        MarketData(
            id="ukraine-ceasefire",
            title="Will Russia and Ukraine agree to a ceasefire in 2025?",
            category="Geopolitics",
            end_date="2025-12-31T23:59:59Z",
            active=True
        ),
        MarketData(
            id="ukraine-peace-june",
            title="Will there be a Russia-Ukraine peace agreement by June 2025?",
            category="Geopolitics",
            end_date="2025-06-30T23:59:59Z",
            active=True
        ),
        MarketData(
            id="champions-league",
            title="Which team will win the 2024-25 UEFA Champions League?",
            category="Sports",
            end_date="2025-06-01T00:00:00Z",
            active=True
        ),
        MarketData(
            id="nba-championship",
            title="Which team will win the 2024-25 NBA Championship?",
            category="NBA",
            end_date="2025-06-15T00:00:00Z",
            active=True
        ),
        MarketData(
            id="trump-conviction",
            title="Will Donald Trump be convicted of a felony in 2025?",
            category="Politics",
            end_date="2025-12-31T23:59:59Z",
            active=True
        ),
        MarketData(
            id="ai-company-ipo",
            title="Will OpenAI or Anthropic go public in 2025?",
            category="Tech",
            end_date="2025-12-31T23:59:59Z",
            active=True
        ),
        MarketData(
            id="recession-2025",
            title="Will the US enter a recession in 2025?",
            category="Economics",
            end_date="2025-12-31T23:59:59Z",
            active=True
        )
    ]


def test_complex_queries():
    """Test complex, ambiguous queries that challenge hardcoded logic"""
    return [
        "Bitcoin moon when?",
        "Fed dovish or hawkish next meeting",
        "Is the war ending soon?",
        "Crypto to the moon this year",
        "Interest rate environment 2025",
        "Will there be peace in Eastern Europe?",
        "Tech IPO market hot or not",
        "Sports betting on championships",
        "Economic downturn coming?",
        "Trump legal troubles outcome"
    ]


def compare_approaches():
    """Compare hardcoded vs LLM-based market matching"""
    markets = get_test_markets()
    queries = test_complex_queries()
    
    # Initialize LLM matcher
    llm_matcher = LLMMarketMatcher()
    
    print("="*100)
    print("COMPARING HARDCODED VS LLM-BASED MARKET MATCHING")
    print("="*100)
    
    for query in queries[:5]:  # Test first 5 queries
        print(f"\n{'='*80}")
        print(f"Query: '{query}'")
        print("="*80)
        
        # Hardcoded approach
        print("\n🔧 HARDCODED APPROACH:")
        hardcoded_scores = []
        for market in markets:
            market_dict = {
                "title": market.title,
                "category": market.category,
                "end_date": market.end_date,
                "active": market.active
            }
            score = calculate_market_relevance(query, market_dict)
            if score > 0.1:
                hardcoded_scores.append((market, score))
        
        hardcoded_scores.sort(key=lambda x: x[1], reverse=True)
        
        if hardcoded_scores:
            for i, (market, score) in enumerate(hardcoded_scores[:3], 1):
                print(f"   {i}. [{score:.3f}] {market.title}")
        else:
            print("   ❌ No relevant markets found")
        
        # LLM approach
        print("\n🤖 LLM-BASED APPROACH:")
        llm_results = llm_matcher.find_best_markets(query, markets, top_k=3)
        
        if llm_results:
            for i, (market, score, reasoning) in enumerate(llm_results, 1):
                print(f"   {i}. [{score:.3f}] {market.title}")
                print(f"      → {reasoning}")
        else:
            print("   ❌ No relevant markets found")


def test_edge_cases():
    """Test edge cases that hardcoded logic struggles with"""
    markets = get_test_markets()
    llm_matcher = LLMMarketMatcher()
    
    print("\n\n" + "="*100)
    print("TESTING EDGE CASES WITH LLM MATCHER")
    print("="*100)
    
    edge_queries = [
        ("What's the deal with interest rates?", "Should understand this is about Fed policy"),
        ("Crypto 📈🚀", "Should understand emoji context about crypto going up"),
        ("War or peace?", "Should understand this is about geopolitical conflicts"),
        ("200k EOY?", "Should understand this is about Bitcoin reaching $200k by end of year"),
        ("Champions of Europe", "Should understand this is about Champions League")
    ]
    
    for query, expected in edge_queries:
        print(f"\n{'='*60}")
        print(f"Query: '{query}'")
        print(f"Expected: {expected}")
        print("-"*60)
        
        results = llm_matcher.find_best_markets(query, markets, top_k=2)
        
        if results:
            for market, score, reasoning in results:
                print(f"[{score:.3f}] {market.title}")
                print(f"   → {reasoning}")
        else:
            print("❌ No matches found")


def test_scalability():
    """Test how LLM approach handles new market types without code changes"""
    print("\n\n" + "="*100)
    print("TESTING SCALABILITY - NEW MARKET TYPES")
    print("="*100)
    
    # Add some novel market types that hardcoded logic wouldn't handle
    novel_markets = [
        MarketData(
            id="quantum-2025",
            title="Will a quantum computer achieve quantum supremacy over GPT-4 in 2025?",
            category="Tech",
            end_date="2025-12-31T23:59:59Z",
            active=True
        ),
        MarketData(
            id="mars-2025",
            title="Will SpaceX successfully land humans on Mars by 2025?",
            category="Space",
            end_date="2025-12-31T23:59:59Z",
            active=True
        ),
        MarketData(
            id="climate-2025",
            title="Will 2025 be the hottest year on record globally?",
            category="Climate",
            end_date="2025-12-31T23:59:59Z",
            active=True
        )
    ]
    
    all_markets = get_test_markets() + novel_markets
    llm_matcher = LLMMarketMatcher()
    
    novel_queries = [
        "quantum computing breakthrough",
        "Mars mission timeline",
        "global warming getting worse?"
    ]
    
    for query in novel_queries:
        print(f"\nQuery: '{query}'")
        print("-"*60)
        
        results = llm_matcher.find_best_markets(query, all_markets, top_k=2)
        
        if results:
            for market, score, reasoning in results:
                print(f"[{score:.3f}] {market.title}")
                print(f"   → {reasoning}")
                
            # Check if it found the novel markets
            if any(m.id.startswith(('quantum', 'mars', 'climate')) for m, _, _ in results):
                print("   ✅ Successfully matched novel market type!")
        else:
            print("❌ No matches found")


if __name__ == "__main__":
    # Run comparisons
    compare_approaches()
    
    # Test edge cases
    test_edge_cases()
    
    # Test scalability
    test_scalability()
    
    print("\n\n" + "="*100)
    print("CONCLUSION")
    print("="*100)
    print("✅ LLM-based matching provides:")
    print("   - Semantic understanding of queries")
    print("   - No hardcoded rules to maintain")
    print("   - Handles novel market types automatically")
    print("   - Explains reasoning for each match")
    print("   - Scales to new domains without code changes")