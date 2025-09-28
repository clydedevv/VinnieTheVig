#!/usr/bin/env python3
"""
Comprehensive LLM Market Matching Tests
Tests all market types, non-matches, and poor matches
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.flows.llm_market_matcher import LLMMarketMatcher, MarketData
import time


def get_test_markets():
    """Get diverse test markets"""
    return [
        # Crypto
        MarketData(
            id="btc-200k",
            title="Will Bitcoin reach $200,000 by end of 2025?",
            category="Crypto",
            end_date="2025-12-31T23:59:59Z",
            active=True,
            market_slug="bitcoin-200k-eoy-2025"
        ),
        MarketData(
            id="eth-10k",
            title="Will Ethereum reach $10,000 in 2025?",
            category="Crypto",
            end_date="2025-12-31T23:59:59Z",
            active=True,
            market_slug="ethereum-10k-2025"
        ),
        
        # Fed/Economics
        MarketData(
            id="fed-cuts",
            title="How many times will the Fed cut rates in 2025?",
            category="Economics",
            end_date="2025-12-31T23:59:59Z",
            active=True,
            market_slug="fed-rate-cuts-2025"
        ),
        MarketData(
            id="fed-march",
            title="Will the Fed cut rates at the March 2025 FOMC meeting?",
            category="Economics",
            end_date="2025-03-19T18:00:00Z",
            active=True,
            market_slug="fed-march-2025-cut"
        ),
        MarketData(
            id="recession",
            title="Will the US enter a recession in 2025?",
            category="Economics",
            end_date="2025-12-31T23:59:59Z",
            active=True,
            market_slug="us-recession-2025"
        ),
        
        # Geopolitical
        MarketData(
            id="ukraine-ceasefire",
            title="Will Russia and Ukraine agree to a ceasefire in 2025?",
            category="Geopolitics",
            end_date="2025-12-31T23:59:59Z",
            active=True,
            market_slug="russia-ukraine-ceasefire-2025"
        ),
        MarketData(
            id="china-taiwan",
            title="Will China invade Taiwan in 2025?",
            category="Geopolitics",
            end_date="2025-12-31T23:59:59Z",
            active=True,
            market_slug="china-taiwan-invasion-2025"
        ),
        
        # Sports
        MarketData(
            id="nba-champ",
            title="Which team will win the 2024-25 NBA Championship?",
            category="NBA",
            end_date="2025-06-15T00:00:00Z",
            active=True,
            market_slug="nba-championship-2025"
        ),
        MarketData(
            id="superbowl",
            title="Which team will win Super Bowl LIX?",
            category="NFL",
            end_date="2025-02-09T23:59:59Z",
            active=True,
            market_slug="superbowl-59-winner"
        ),
        
        # Tech
        MarketData(
            id="openai-ipo",
            title="Will OpenAI go public (IPO) in 2025?",
            category="Tech",
            end_date="2025-12-31T23:59:59Z",
            active=True,
            market_slug="openai-ipo-2025"
        ),
        MarketData(
            id="gpt5",
            title="Will OpenAI release GPT-5 in 2025?",
            category="Tech",
            end_date="2025-12-31T23:59:59Z",
            active=True,
            market_slug="gpt5-release-2025"
        ),
        
        # Politics
        MarketData(
            id="trump-conviction",
            title="Will Donald Trump be convicted of a felony in 2025?",
            category="Politics",
            end_date="2025-12-31T23:59:59Z",
            active=True,
            market_slug="trump-conviction-2025"
        ),
        MarketData(
            id="biden-finish",
            title="Will Joe Biden finish his second term as President?",
            category="Politics",
            end_date="2029-01-20T12:00:00Z",
            active=True,
            market_slug="biden-finish-term"
        )
    ]


def test_all_market_types():
    """Test queries for all market types"""
    print("="*100)
    print("TESTING ALL MARKET TYPES")
    print("="*100)
    
    matcher = LLMMarketMatcher()
    markets = get_test_markets()
    
    test_queries = [
        # Crypto (not just Bitcoin)
        ("eth to 10k this cycle", "ethereum-10k-2025", "Ethereum price query"),
        ("ethereum moon wen", "ethereum-10k-2025", "Ethereum slang query"),
        
        # Fed/Economics
        ("jpow gonna cut or what", "fed-rate-cuts-2025", "Fed chair reference"),
        ("march fomc gonna be spicy", "fed-march-2025-cut", "Specific Fed meeting"),
        ("recession cancelled", "us-recession-2025", "Economic optimism"),
        ("soft landing cope", "us-recession-2025", "Economic skepticism"),
        
        # Geopolitical
        ("ukraine thing ending soon?", "russia-ukraine-ceasefire-2025", "Ukraine war"),
        ("china taiwan situation escalating", "china-taiwan-invasion-2025", "China-Taiwan"),
        
        # Sports
        ("celtics taking it all", "nba-championship-2025", "NBA prediction"),
        ("chiefs back to back", "superbowl-59-winner", "NFL prediction"),
        
        # Tech
        ("openai ipo wen", "openai-ipo-2025", "Tech IPO query"),
        ("gpt5 dropping this year?", "gpt5-release-2025", "AI model release"),
        
        # Politics
        ("trump going to jail?", "trump-conviction-2025", "Trump legal"),
        ("biden gonna make it", "biden-finish-term", "Biden presidency"),
    ]
    
    results = {"correct": 0, "total": 0, "by_category": {}}
    
    for query, expected_slug, description in test_queries:
        print(f"\n{'='*80}")
        print(f"Query: \"{query}\" ({description})")
        print(f"Expected: {expected_slug}")
        
        try:
            matches = matcher.find_best_markets(query, markets, top_k=3)
            results["total"] += 1
            
            category = description.split()[0]
            if category not in results["by_category"]:
                results["by_category"][category] = {"correct": 0, "total": 0}
            results["by_category"][category]["total"] += 1
            
            if matches:
                top_match = matches[0]
                market, score, reasoning = top_match
                
                is_correct = market.market_slug == expected_slug
                if is_correct:
                    results["correct"] += 1
                    results["by_category"][category]["correct"] += 1
                    status = "✅ CORRECT"
                else:
                    status = "❌ WRONG"
                
                print(f"\nResult: {status}")
                print(f"Match: [{score:.3f}] {market.title}")
                print(f"Reasoning: {reasoning[:150]}...")
                
                if len(matches) > 1 and not is_correct:
                    print("\nOther matches:")
                    for i, (m, s, r) in enumerate(matches[1:3], 2):
                        print(f"  {i}. [{s:.3f}] {m.title}")
                        if m.market_slug == expected_slug:
                            print(f"     ⚠️  Expected market was #{i}")
            else:
                print("❌ No matches found")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            results["total"] += 1
        
        time.sleep(0.5)
    
    # Print summary
    print("\n" + "="*100)
    print("SUMMARY BY CATEGORY")
    print("="*100)
    for category, stats in results["by_category"].items():
        accuracy = stats["correct"] / stats["total"] * 100 if stats["total"] > 0 else 0
        print(f"{category}: {stats['correct']}/{stats['total']} ({accuracy:.1f}%)")
    
    overall_accuracy = results["correct"] / results["total"] * 100 if results["total"] > 0 else 0
    print(f"\nOverall: {results['correct']}/{results['total']} ({overall_accuracy:.1f}%)")
    
    return results


def test_no_match_queries():
    """Test queries that should have no good matches"""
    print("\n\n" + "="*100)
    print("TESTING QUERIES WITH NO GOOD MATCHES")
    print("="*100)
    
    matcher = LLMMarketMatcher()
    markets = get_test_markets()
    
    no_match_queries = [
        ("taylor swift travis kelce wedding date", "Celebrity gossip - no market"),
        ("will aliens be discovered", "Aliens - no market"),
        ("apple stock price tomorrow", "Day trading - no market"),
        ("weather in miami next week", "Weather - no market"),
        ("best pizza in nyc", "Food opinion - no market"),
        ("how to make money fast", "Get rich scheme - no market"),
        ("covid coming back?", "COVID - no relevant 2025 market"),
        ("dogecoin to $1", "Dogecoin - no market"),
        ("world cup 2026 winner", "Wrong year - 2026 not 2025"),
        ("will i get a girlfriend", "Personal - no market"),
    ]
    
    for query, description in no_match_queries:
        print(f"\n{'='*60}")
        print(f"Query: \"{query}\"")
        print(f"Note: {description}")
        
        try:
            matches = matcher.find_best_markets(query, markets, top_k=2)
            
            if matches:
                top_match = matches[0]
                market, score, reasoning = top_match
                
                if score < 0.3:
                    print(f"✅ Low confidence: [{score:.3f}] {market.title}")
                    print(f"   Good - recognizes poor match")
                else:
                    print(f"⚠️  High confidence on poor match: [{score:.3f}] {market.title}")
                    print(f"   Reasoning: {reasoning[:100]}...")
            else:
                print("✅ No matches found (correct behavior)")
                
        except Exception as e:
            print(f"Error: {e}")
        
        time.sleep(0.5)


def test_ambiguous_queries():
    """Test highly ambiguous queries"""
    print("\n\n" + "="*100)
    print("TESTING AMBIGUOUS QUERIES")
    print("="*100)
    
    matcher = LLMMarketMatcher()
    markets = get_test_markets()
    
    ambiguous_queries = [
        ("moon", "Could be crypto or space"),
        ("crash", "Could be market crash or accident"),
        ("pump it", "Could be crypto or Fed policy"),
        ("its over", "Could be anything"),
        ("wagmi", "Crypto slang - we're all gonna make it"),
        ("lfg", "Let's go - too vague"),
        ("big if true", "Meme - no context"),
        ("soon", "No context at all"),
        ("👀", "Just eyes emoji"),
        ("?????", "Just question marks"),
    ]
    
    for query, description in ambiguous_queries:
        print(f"\n{'='*60}")
        print(f"Query: \"{query}\" ({description})")
        
        try:
            matches = matcher.find_best_markets(query, markets[:5], top_k=2)  # Limit markets for speed
            
            if matches:
                for i, (market, score, reasoning) in enumerate(matches, 1):
                    print(f"{i}. [{score:.3f}] {market.title[:50]}...")
                    if score < 0.5:
                        print(f"   ✅ Appropriately low confidence")
                    else:
                        print(f"   ⚠️  High confidence on vague query")
            else:
                print("No matches (might be appropriate)")
                
        except Exception as e:
            print(f"Error: {e}")
        
        time.sleep(0.5)


def test_close_but_wrong():
    """Test queries that are close to a market but not quite right"""
    print("\n\n" + "="*100)
    print("TESTING CLOSE BUT WRONG MATCHES")
    print("="*100)
    
    matcher = LLMMarketMatcher()
    markets = get_test_markets()
    
    close_queries = [
        ("bitcoin 300k", "Wrong price - we have 200k not 300k"),
        ("fed raising rates", "Wrong direction - we have cutting not raising"),
        ("ethereum $5k", "Wrong price - we have 10k not 5k"),
        ("trump president 2025", "Wrong - we have conviction not presidency"),
        ("ukraine winning war", "Different framing - we have ceasefire not winning"),
        ("chiefs winning NBA", "Wrong sport - Chiefs are NFL not NBA"),
        ("openai bankrupt", "Opposite - we have IPO not bankruptcy"),
        ("bitcoin crashing to zero", "Opposite direction - we have moon not crash"),
    ]
    
    for query, description in close_queries:
        print(f"\n{'='*60}")
        print(f"Query: \"{query}\"")
        print(f"Issue: {description}")
        
        try:
            matches = matcher.find_best_markets(query, markets, top_k=2)
            
            if matches:
                market, score, reasoning = matches[0]
                print(f"\nMatch: [{score:.3f}] {market.title}")
                print(f"Reasoning: {reasoning[:150]}...")
                
                if score > 0.7:
                    print("⚠️  High confidence despite mismatch")
                else:
                    print("✅ Appropriately lower confidence")
                    
        except Exception as e:
            print(f"Error: {e}")
        
        time.sleep(0.5)


if __name__ == "__main__":
    # Test all market types
    results = test_all_market_types()
    
    # Test queries with no good matches
    test_no_match_queries()
    
    # Test ambiguous queries
    test_ambiguous_queries()
    
    # Test close but wrong matches
    test_close_but_wrong()
    
    print("\n\n" + "="*100)
    print("COMPREHENSIVE TESTING COMPLETE")
    print("="*100)