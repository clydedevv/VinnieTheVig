#!/usr/bin/env python3
"""
Test Market Matching Improvements
Validates that our algorithm improvements handle edge cases correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tests.unit.test_market_matching_standalone import calculate_market_relevance


def test_improvements():
    """Test specific improvements made to the algorithm"""
    print("=" * 80)
    print("TESTING MARKET MATCHING IMPROVEMENTS")
    print("=" * 80)
    
    # Test case 1: Federal Reserve phrase matching
    print("\n1. Testing Federal Reserve phrase matching improvements:")
    fed_market = {
        "title": "How many times will the Fed cut rates in 2025?",
        "category": "Economics",
        "end_date": "2025-12-31T23:59:59Z",
        "active": True
    }
    
    queries = [
        ("Federal Reserve interest rates", "Should match via synonyms and phrase"),
        ("Fed monetary policy", "Should match via Fed synonym"),
        ("interest rate decisions", "Should match via rate/rates synonyms")
    ]
    
    for query, expected in queries:
        score = calculate_market_relevance(query, fed_market)
        print(f"  Query: '{query}'")
        print(f"  Score: {score:.3f} - {expected}")
        print(f"  {'✅ PASS' if score >= 0.5 else '❌ FAIL'}")
    
    # Test case 2: Bitcoin price level handling
    print("\n\n2. Testing Bitcoin price level improvements:")
    btc_200k_market = {
        "title": "Will Bitcoin reach $200,000 by end of 2025?",
        "category": "Crypto",
        "end_date": "2025-12-31T23:59:59Z",
        "active": True
    }
    
    btc_150k_market = {
        "title": "Will Bitcoin hit $150,000 by June 2025?",
        "category": "Crypto",
        "end_date": "2025-06-30T23:59:59Z",
        "active": True
    }
    
    query = "Bitcoin reaching $200k this year"
    score_200k = calculate_market_relevance(query, btc_200k_market)
    score_150k = calculate_market_relevance(query, btc_150k_market)
    
    print(f"  Query: '{query}'")
    print(f"  200k market score: {score_200k:.3f}")
    print(f"  150k market score: {score_150k:.3f}")
    print(f"  {'✅ PASS' if score_200k > score_150k else '❌ FAIL'} - 200k should score higher")
    
    # Test case 3: Time-sensitive matching
    print("\n\n3. Testing time-sensitive improvements:")
    query_year = "Bitcoin price this year"
    query_june = "Bitcoin price by June"
    
    score_year_eoy = calculate_market_relevance(query_year, btc_200k_market)
    score_year_june = calculate_market_relevance(query_year, btc_150k_market)
    
    score_june_eoy = calculate_market_relevance(query_june, btc_200k_market)
    score_june_june = calculate_market_relevance(query_june, btc_150k_market)
    
    print(f"  'This year' query:")
    print(f"    End-of-year market: {score_year_eoy:.3f}")
    print(f"    June market: {score_year_june:.3f}")
    print(f"    {'✅ PASS' if score_year_eoy > score_year_june else '❌ FAIL'} - EOY should score higher for 'this year'")
    
    print(f"\n  'By June' query:")
    print(f"    End-of-year market: {score_june_eoy:.3f}")
    print(f"    June market: {score_june_june:.3f}")
    print(f"    {'✅ PASS' if score_june_june > score_june_eoy else '❌ FAIL'} - June should score higher for 'by June'")
    
    # Test case 4: Phrase-level matching
    print("\n\n4. Testing phrase-level matching:")
    champions_market = {
        "title": "Which team will win the 2024-25 UEFA Champions League?",
        "category": "Sports",
        "end_date": "2025-06-01T00:00:00Z",
        "active": True
    }
    
    queries = [
        ("Champions League", "Should get phrase bonus"),
        ("champions", "Should match but no phrase bonus"),
        ("league", "Should match but lower score")
    ]
    
    for query, expected in queries:
        score = calculate_market_relevance(query, champions_market)
        print(f"  Query: '{query}'")
        print(f"  Score: {score:.3f} - {expected}")
    
    # Test case 5: Synonym expansion
    print("\n\n5. Testing synonym expansion:")
    btc_market = {
        "title": "Will Bitcoin hit $120,000 in 2025?",
        "category": "Crypto",
        "end_date": "2025-12-31T23:59:59Z",
        "active": True
    }
    
    queries = [
        ("BTC price", "Should match via BTC->Bitcoin synonym"),
        ("crypto reaching 120k", "Should match via crypto->bitcoin synonym"),
        ("Bitcoin hit 120k", "Should match directly")
    ]
    
    for query, expected in queries:
        score = calculate_market_relevance(query, btc_market)
        print(f"  Query: '{query}'")
        print(f"  Score: {score:.3f} - {expected}")
        print(f"  {'✅ PASS' if score >= 0.7 else '❌ FAIL'}")
    
    print("\n" + "=" * 80)
    print("IMPROVEMENT TEST COMPLETE")
    print("=" * 80)


def test_edge_cases():
    """Test edge cases and potential failure modes"""
    print("\n\nTESTING EDGE CASES")
    print("=" * 80)
    
    # Edge case 1: Very short queries
    print("\n1. Very short queries:")
    markets = [
        {
            "title": "Will Bitcoin hit $120,000 in 2025?",
            "category": "Crypto",
            "end_date": "2025-12-31T23:59:59Z",
            "active": True
        },
        {
            "title": "Which team will win the 2024-25 NBA Championship?",
            "category": "NBA",
            "end_date": "2025-06-15T00:00:00Z",
            "active": True
        }
    ]
    
    short_queries = ["Bitcoin", "NBA", "2025", "win"]
    
    for query in short_queries:
        print(f"\n  Query: '{query}'")
        for market in markets:
            score = calculate_market_relevance(query, market)
            if score > 0.1:
                print(f"    [{score:.3f}] {market['title'][:50]}...")
    
    # Edge case 2: Queries with numbers
    print("\n\n2. Queries with price numbers:")
    number_queries = [
        "200k",
        "$200,000",
        "200000",
        "bitcoin 200k",
        "BTC $200k"
    ]
    
    btc_200k_market = {
        "title": "Will Bitcoin reach $200,000 by end of 2025?",
        "category": "Crypto",
        "end_date": "2025-12-31T23:59:59Z",
        "active": True
    }
    
    for query in number_queries:
        score = calculate_market_relevance(query, btc_200k_market)
        print(f"  Query: '{query}' -> Score: {score:.3f}")
    
    # Edge case 3: Mixed case and punctuation
    print("\n\n3. Mixed case and punctuation:")
    test_queries = [
        "BITCOIN PRICE!!!",
        "fed RATE cut?",
        "Champions-League",
        "russia/ukraine war"
    ]
    
    for query in test_queries:
        print(f"\n  Query: '{query}'")
        # Test against first few markets
        for market in markets[:2]:
            score = calculate_market_relevance(query, market)
            if score > 0.1:
                print(f"    [{score:.3f}] {market['title'][:50]}...")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    test_improvements()
    test_edge_cases()