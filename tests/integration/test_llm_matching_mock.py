#!/usr/bin/env python3
"""
Test LLM Market Matching with Mock Data
Tests the pipeline with realistic data without requiring database connection
"""
import sys
import os
# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.flows.llm_market_matcher import LLMMarketMatcher, MarketData
from src.flows.dspy_enhanced_aigg_flow import DSPyEnhancedAIGGFlow, Market
import time


def get_mock_polymarket_data():
    """Mock Polymarket data based on real markets"""
    return [
        Market(
            id="0xbtc200k",
            title="Will Bitcoin reach $200,000 by end of 2025?",
            category="Crypto",
            end_date="2025-12-31T23:59:59Z",
            active=True,
            relevance_score=0.0,
            market_slug="bitcoin-200k-eoy-2025"
        ),
        Market(
            id="0xbtc150k",
            title="Will Bitcoin hit $150,000 by June 2025?",
            category="Crypto", 
            end_date="2025-06-30T23:59:59Z",
            active=True,
            relevance_score=0.0,
            market_slug="bitcoin-150k-june-2025"
        ),
        Market(
            id="0xfedcuts",
            title="How many times will the Fed cut rates in 2025?",
            category="Economics",
            end_date="2025-12-31T23:59:59Z",
            active=True,
            relevance_score=0.0,
            market_slug="fed-rate-cuts-2025"
        ),
        Market(
            id="0xfedmarch",
            title="Will the Fed cut rates at the March 2025 FOMC meeting?",
            category="Economics",
            end_date="2025-03-19T18:00:00Z",
            active=True,
            relevance_score=0.0,
            market_slug="fed-march-2025-cut"
        ),
        Market(
            id="0xukrpeace",
            title="Will Russia and Ukraine agree to a ceasefire in 2025?",
            category="Geopolitics",
            end_date="2025-12-31T23:59:59Z",
            active=True,
            relevance_score=0.0,
            market_slug="russia-ukraine-ceasefire-2025"
        ),
        Market(
            id="0xukrjune",
            title="Will there be a Russia-Ukraine peace agreement by June 2025?",
            category="Geopolitics",
            end_date="2025-06-30T23:59:59Z",
            active=True,
            relevance_score=0.0,
            market_slug="ukraine-peace-june-2025"
        ),
        Market(
            id="0xnba",
            title="Which team will win the 2024-25 NBA Championship?",
            category="NBA",
            end_date="2025-06-15T00:00:00Z",
            active=True,
            relevance_score=0.0,
            market_slug="nba-championship-2025"
        ),
        Market(
            id="0xchampl",
            title="Which team will win the 2024-25 UEFA Champions League?",
            category="Sports",
            end_date="2025-06-01T00:00:00Z",
            active=True,
            relevance_score=0.0,
            market_slug="champions-league-2025"
        ),
        Market(
            id="0xrecession",
            title="Will the US enter a recession in 2025?",
            category="Economics",
            end_date="2025-12-31T23:59:59Z",
            active=True,
            relevance_score=0.0,
            market_slug="us-recession-2025"
        ),
        Market(
            id="0xopenai",
            title="Will OpenAI go public (IPO) in 2025?",
            category="Tech",
            end_date="2025-12-31T23:59:59Z",
            active=True,
            relevance_score=0.0,
            market_slug="openai-ipo-2025"
        )
    ]


def test_realistic_queries_with_llm():
    """Test realistic 2025 queries using LLM matching"""
    print("="*100)
    print("TESTING LLM MARKET MATCHING WITH REALISTIC 2025 QUERIES")
    print("="*100)
    
    # Initialize LLM matcher
    matcher = LLMMarketMatcher()
    
    # Get mock markets
    mock_markets = get_mock_polymarket_data()
    
    # Convert to MarketData for LLM matcher
    market_data = []
    for m in mock_markets:
        market_data.append(MarketData(
            id=m.id,
            title=m.title,
            category=m.category,
            end_date=m.end_date,
            active=m.active,
            market_slug=m.market_slug
        ))
    
    # Realistic test queries
    test_cases = [
        # Crypto queries
        ("btc 200k eoy or nah", "bitcoin-200k-eoy-2025", "Casual crypto speculation"),
        ("bitcoin really gonna hit 200k this year lmao", "bitcoin-200k-eoy-2025", "Skeptical crypto query"),
        ("gm bitcoin 150k by summer?", "bitcoin-150k-june-2025", "Time-specific crypto query"),
        ("digital gold to 200k thesis still intact fr", "bitcoin-200k-eoy-2025", "Crypto narrative language"),
        
        # Fed queries
        ("jpow gonna cut or what", "fed-rate-cuts-2025", "Casual Fed reference"),
        ("march fomc gonna be spicy", "fed-march-2025-cut", "Specific Fed meeting"),
        ("fed pivot wen", "fed-rate-cuts-2025", "When will Fed pivot"),
        
        # Geopolitical
        ("ukraine thing ending anytime soon?", "russia-ukraine-ceasefire-2025", "Casual war reference"),
        ("peace talks actually happening or just rumors", "ukraine-peace-june-2025", "Peace speculation"),
        
        # Sports
        ("celtics taking it all no cap", "nba-championship-2025", "NBA prediction"),
        ("who's winning champions league liverpool looking good", "champions-league-2025", "Soccer query"),
        
        # Economic
        ("soft landing cope continues", "us-recession-2025", "Economic skepticism"),
        ("recession cancelled", "us-recession-2025", "Economic optimism"),
        
        # Tech
        ("openai ipo this year for sure", "openai-ipo-2025", "Tech IPO speculation"),
    ]
    
    results = []
    correct = 0
    
    for i, (query, expected_slug, description) in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"Test {i}/{len(test_cases)}: {description}")
        print(f"Query: \"{query}\"")
        print(f"Expected: {expected_slug}")
        print("-"*80)
        
        try:
            # Find best matches using LLM
            matches = matcher.find_best_markets(query, market_data, top_k=3)
            
            if matches:
                top_match = matches[0]
                market, score, reasoning = top_match
                
                is_correct = market.market_slug == expected_slug
                if is_correct:
                    correct += 1
                    status = "✅ CORRECT"
                else:
                    status = "❌ WRONG"
                
                print(f"\nResult: {status}")
                print(f"Match: [{score:.3f}] {market.title}")
                print(f"Slug: {market.market_slug}")
                print(f"Reasoning: {reasoning}")
                
                results.append({
                    "query": query,
                    "expected": expected_slug,
                    "actual": market.market_slug,
                    "score": score,
                    "correct": is_correct
                })
                
                # Show other top matches
                if len(matches) > 1:
                    print("\nOther matches:")
                    for j, (m, s, r) in enumerate(matches[1:3], 2):
                        print(f"  {j}. [{s:.3f}] {m.title[:50]}...")
            else:
                print("❌ No matches found")
                results.append({
                    "query": query,
                    "expected": expected_slug,
                    "actual": None,
                    "score": 0.0,
                    "correct": False
                })
                
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append({
                "query": query,
                "expected": expected_slug,
                "actual": None,
                "score": 0.0,
                "correct": False,
                "error": str(e)
            })
        
        # Don't overwhelm the API
        time.sleep(0.5)
    
    # Summary
    print("\n" + "="*100)
    print("TEST SUMMARY")
    print("="*100)
    print(f"Total tests: {len(test_cases)}")
    print(f"Correct: {correct} ({correct/len(test_cases)*100:.1f}%)")
    print(f"Incorrect: {len(test_cases) - correct}")
    
    # Show failures
    failures = [r for r in results if not r["correct"]]
    if failures:
        print("\nFailed queries:")
        for f in failures:
            print(f"  - \"{f['query']}\"")
            print(f"    Expected: {f['expected']}")
            print(f"    Got: {f['actual']}")
    
    return results


def test_edge_cases():
    """Test edge cases and ambiguous queries"""
    print("\n\n" + "="*100)
    print("TESTING EDGE CASES")
    print("="*100)
    
    matcher = LLMMarketMatcher()
    mock_markets = get_mock_polymarket_data()
    
    # Convert to MarketData
    market_data = []
    for m in mock_markets[:5]:  # Use subset for edge cases
        market_data.append(MarketData(
            id=m.id,
            title=m.title,
            category=m.category,
            end_date=m.end_date,
            active=m.active,
            market_slug=m.market_slug
        ))
    
    edge_cases = [
        ("200k programmed", "Bitcoin 200k meme"),
        ("wen peace", "When peace?"),
        ("fed cooked", "Fed in trouble"),
        ("number go up", "Crypto bullish"),
        ("it's so over (economically speaking)", "Economic pessimism"),
        ("we are so back (bitcoin edition)", "Bitcoin optimism"),
    ]
    
    for query, description in edge_cases:
        print(f"\nQuery: \"{query}\" ({description})")
        
        try:
            matches = matcher.find_best_markets(query, market_data, top_k=1)
            
            if matches:
                market, score, reasoning = matches[0]
                print(f"Match: [{score:.3f}] {market.title[:50]}...")
                print(f"Reasoning: {reasoning}")
            else:
                print("No match found")
                
        except Exception as e:
            print(f"Error: {e}")
        
        time.sleep(0.5)


if __name__ == "__main__":
    # Test with realistic queries
    results = test_realistic_queries_with_llm()
    
    # Test edge cases
    test_edge_cases()
    
    print("\n\n" + "="*100)
    print("LLM MARKET MATCHING TEST COMPLETE")
    print("="*100)
    
    # Final assessment
    if results:
        accuracy = sum(1 for r in results if r["correct"]) / len(results)
        if accuracy >= 0.8:
            print("✅ LLM matching is working well! Ready for production.")
        elif accuracy >= 0.6:
            print("⚠️  LLM matching needs some tuning but is functional.")
        else:
            print("❌ LLM matching needs significant improvement.")