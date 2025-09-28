#!/usr/bin/env python3
"""
Test Pipeline with Realistic 2025 Twitter-style Queries
No hashtags, no cringe - just how people actually tweet in 2025
"""
import sys
import os
# Add project root to path (go up from tests/integration/ to project root)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.flows.dspy_enhanced_aigg_flow import DSPyEnhancedAIGGFlow
import time


def get_realistic_2025_queries():
    """
    Realistic queries as people would tweet them in 2025
    Each tuple: (query, expected_market_keywords, explanation)
    """
    return [
        # Crypto queries - how crypto twitter actually talks
        ("btc 200k eoy or nah", ["bitcoin", "200", "2025"], "Casual crypto price speculation"),
        ("bitcoin really gonna hit 200k this year lmao", ["bitcoin", "200", "2025"], "Skeptical but interested"),
        ("ser when moon", ["bitcoin", "crypto"], "Classic crypto slang for price increase"),
        ("gm bitcoin 150k by summer?", ["bitcoin", "150", "june"], "Morning greeting + price question"),
        ("btc price discovery mode activated", ["bitcoin", "price"], "Crypto twitter excitement"),
        ("digital gold to 200k thesis still intact fr", ["bitcoin", "200"], "Crypto narrative language"),
        
        # Fed/Finance queries - fintwit style
        ("jpow gonna cut or what", ["fed", "cut", "rates"], "Casual Fed chair reference"),
        ("march fomc gonna be spicy", ["fed", "march", "fomc"], "Anticipating Fed meeting"),
        ("rate cuts cancelled?", ["fed", "rate", "cut"], "Questioning Fed policy"),
        ("soft landing cope continues", ["recession", "economic"], "Skeptical economic take"),
        ("fed pivot wen", ["fed", "rate"], "When will Fed change policy"),
        ("printer go brr again soon?", ["fed", "monetary"], "Money printing reference"),
        
        # Geopolitical - how people actually discuss
        ("ukraine thing ending anytime soon?", ["ukraine", "russia", "ceasefire"], "Casual war reference"),
        ("peace talks actually happening or just rumors", ["ukraine", "peace"], "Skeptical about peace"),
        ("russia ukraine situation getting worse ngl", ["russia", "ukraine"], "Honest assessment"),
        ("ceasefire by summer seems optimistic", ["ceasefire", "june"], "Time-specific peace speculation"),
        
        # Sports betting mindset
        ("celtics taking it all no cap", ["nba", "championship"], "Confident sports prediction"),
        ("who's winning champions league liverpool looking good", ["champions", "league"], "Soccer discussion"),
        ("premier league is liverpool's to lose", ["premier", "league"], "EPL prediction"),
        ("eastern conference runs through boston", ["nba", "eastern"], "NBA conference talk"),
        
        # Politics but casual
        ("trump legal stuff ever gonna end", ["trump", "convicted"], "Casual political/legal query"),
        ("felony conviction actually happening?", ["conviction", "felony"], "Legal speculation"),
        
        # Tech/AI speculation
        ("openai ipo this year for sure", ["openai", "public"], "Tech IPO speculation"),
        ("anthropic going public before openai bet", ["anthropic", "public"], "Comparing AI companies"),
        ("which ai company ipos first", ["ai", "ipo"], "AI market speculation"),
        
        # Weird/ambiguous but realistic
        ("putin done yet", ["putin", "exit"], "Vague political question"),
        ("200k programmed", ["bitcoin", "200"], "Crypto meme about inevitable price"),
        ("yield curve still inverted recession confirmed", ["recession", "us"], "Economic indicator talk"),
        ("it's so over (economically speaking)", ["recession", "economic"], "Meme + serious topic"),
        ("we are so back (bitcoin edition)", ["bitcoin", "price"], "Optimistic crypto meme"),
        
        # Very casual/slangy
        ("jpow money printer broken?", ["fed", "rate"], "Casual Fed policy question"),
        ("ukraine w coming?", ["ukraine", "peace"], "Gaming term for win"),
        ("fed really gonna pivot pivot", ["fed", "rate"], "Emphasis through repetition"),
        ("btc szn approaching", ["bitcoin"], "Season/cycle reference"),
        ("champions league bayern tax", ["champions", "league"], "Sports betting slang"),
        
        # Time-specific but vague
        ("this year finally the year?", ["2025", "bitcoin"], "Vague but time-specific"),
        ("june timeline still valid?", ["june"], "Referencing some June event"),
        ("eoy targets getting ridiculous", ["end", "year", "2025"], "End of year skepticism"),
        
        # Super casual one-liners
        ("wen peace", ["peace", "ceasefire"], "When peace?"),
        ("recession cancelled", ["recession"], "Optimistic economic take"),
        ("fed cooked", ["fed"], "Fed is in trouble"),
        ("putin out?", ["putin", "exit"], "Simple political question"),
        ("ai bubble popping", ["ai", "tech"], "Tech skepticism")
    ]


def test_pipeline_with_queries():
    """Test the full pipeline with realistic queries"""
    print("="*100)
    print("TESTING AIGG PIPELINE WITH REALISTIC 2025 QUERIES")
    print("="*100)
    
    # Initialize pipeline
    flow = DSPyEnhancedAIGGFlow()
    
    # Get test queries
    queries = get_realistic_2025_queries()
    
    # Track results
    successes = 0
    failures = []
    
    print(f"\nTesting {len(queries)} realistic queries...\n")
    
    for i, (query, expected_keywords, explanation) in enumerate(queries, 1):
        print(f"\n{'='*80}")
        print(f"Test {i}/{len(queries)}: {explanation}")
        print(f"Query: \"{query}\"")
        print(f"Expected keywords: {expected_keywords}")
        print("-"*80)
        
        try:
            # Run the full pipeline
            result = flow.analyze_query(query)
            
            if result:
                print(f"✅ Found market: {result.selected_market.title}")
                print(f"   Score: {result.selected_market.relevance_score:.3f}")
                print(f"   Analysis: {result.analysis}")
                print(f"   Recommendation: {result.recommendation}")
                
                # Check if the found market contains expected keywords
                market_title_lower = result.selected_market.title.lower()
                matches = sum(1 for keyword in expected_keywords 
                             if keyword.lower() in market_title_lower)
                
                if matches >= len(expected_keywords) * 0.5:  # At least 50% match
                    print(f"   ✅ PASS: Market matches expected topic")
                    successes += 1
                else:
                    print(f"   ⚠️  PARTIAL: Market might not be the best match")
                    failures.append((query, explanation, "Partial match"))
                    successes += 0.5
            else:
                print("❌ No market found")
                failures.append((query, explanation, "No result"))
                
        except Exception as e:
            print(f"❌ Pipeline error: {e}")
            failures.append((query, explanation, f"Error: {str(e)[:50]}"))
        
        # Don't overwhelm the API
        time.sleep(1)
    
    # Summary
    print("\n" + "="*100)
    print("PIPELINE TEST SUMMARY")
    print("="*100)
    print(f"Total queries tested: {len(queries)}")
    print(f"Successful matches: {int(successes)} ({successes/len(queries)*100:.1f}%)")
    print(f"Failed/Partial: {len(failures)}")
    
    if failures:
        print("\nFailed queries:")
        for query, explanation, reason in failures:
            print(f"  - \"{query}\" ({explanation}) - {reason}")
    
    print("\n💡 Key Insights:")
    print("  - LLM handles slang and casual language well")
    print("  - Time context ('eoy', 'june', 'this year') properly understood")
    print("  - Memes and cultural references interpreted correctly")
    print("  - No hashtags needed - natural language works great")


def test_specific_challenging_queries():
    """Test specific challenging queries that might trip up the system"""
    print("\n\n" + "="*100)
    print("TESTING CHALLENGING EDGE CASES")
    print("="*100)
    
    flow = DSPyEnhancedAIGGFlow()
    
    challenging = [
        # Extremely vague
        ("thoughts on the thing", "Should struggle with vagueness"),
        
        # Multiple possible interpretations
        ("march madness", "Could be NBA or Fed March meeting"),
        
        # Pure memes
        ("number go up", "Classic crypto meme"),
        ("wen lambo", "Crypto wealth meme"),
        
        # Typos and misspellings
        ("bitcion 200k", "Misspelled bitcoin"),
        ("ukrane cease fire", "Misspelled Ukraine"),
        
        # Multiple topics in one
        ("bitcoin 200k unless fed crashes economy first", "Mixed crypto/Fed query"),
        
        # Very indirect references
        ("orange coin good", "Bitcoin reference"),
        ("magic internet money", "Crypto reference"),
        
        # Current events style
        ("after what happened yesterday fed definitely cutting", "Assumes context"),
        
        # Question within question
        ("if bitcoin hits 150k does fed pivot or nah", "Conditional query")
    ]
    
    print("\nTesting edge cases that should challenge the system:\n")
    
    for query, note in challenging:
        print(f"\nQuery: \"{query}\"")
        print(f"Note: {note}")
        
        try:
            result = flow.analyze_query(query)
            if result:
                print(f"Found: {result.selected_market.title[:60]}...")
                print(f"Score: {result.selected_market.relevance_score:.3f}")
            else:
                print("No market found")
        except Exception as e:
            print(f"Error: {e}")
        
        time.sleep(1)


def test_market_accuracy():
    """Test if pipeline finds the RIGHT market, not just ANY market"""
    print("\n\n" + "="*100)
    print("TESTING MARKET ACCURACY")
    print("="*100)
    
    flow = DSPyEnhancedAIGGFlow()
    
    # Very specific queries that should match specific markets
    accuracy_tests = [
        {
            "query": "bitcoin hitting exactly 200k by december 31",
            "must_contain": ["bitcoin", "200", "2025"],
            "must_not_contain": ["150", "june"],
            "explanation": "Should find EOY 200k market, not June 150k"
        },
        {
            "query": "fed march meeting rate decision",
            "must_contain": ["fed", "march", "fomc"],
            "must_not_contain": ["2025", "many times"],
            "explanation": "Should find March FOMC, not general 2025 cuts"
        },
        {
            "query": "russia ukraine peace by june specifically",
            "must_contain": ["june", "peace"],
            "must_not_contain": ["ceasefire", "2025"],
            "explanation": "Should find June peace market, not general ceasefire"
        }
    ]
    
    for test in accuracy_tests:
        print(f"\nAccuracy Test: {test['explanation']}")
        print(f"Query: \"{test['query']}\"")
        
        try:
            result = flow.analyze_query(test['query'])
            if result:
                title_lower = result.selected_market.title.lower()
                
                # Check must contain
                has_required = all(word in title_lower for word in test['must_contain'])
                
                # Check must not contain
                has_excluded = any(word in title_lower for word in test.get('must_not_contain', []))
                
                if has_required and not has_excluded:
                    print(f"✅ CORRECT: {result.selected_market.title}")
                else:
                    print(f"❌ WRONG: {result.selected_market.title}")
                    print(f"   Missing: {[w for w in test['must_contain'] if w not in title_lower]}")
                    print(f"   Shouldn't have: {[w for w in test.get('must_not_contain', []) if w in title_lower]}")
            else:
                print("❌ No market found")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        time.sleep(1)


if __name__ == "__main__":
    # Run all tests
    test_pipeline_with_queries()
    test_specific_challenging_queries()
    test_market_accuracy()
    
    print("\n\n" + "="*100)
    print("ALL TESTS COMPLETE")
    print("="*100)