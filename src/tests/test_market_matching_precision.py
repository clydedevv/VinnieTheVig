#!/usr/bin/env python3
"""
Market Matching Precision Test
Test and improve the market matching algorithm to ensure the most relevant market ranks #1
"""
import requests
import json
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

# Server configuration
SERVER_IP = "37.27.54.184"
API_PORT = 8001
BASE_URL = f"http://{SERVER_IP}:{API_PORT}"

@dataclass
class TestCase:
    query: str
    expected_keywords: List[str]  # Keywords that should appear in top result
    expected_category: str = None
    description: str = ""

# Define test cases for different types of queries
TEST_CASES = [
    TestCase(
        query="Will Trump win 2024 election",
        expected_keywords=["trump", "2024", "election", "win"],
        expected_category="US-current-affairs",
        description="Political prediction - should find Trump 2024 election markets"
    ),
    TestCase(
        query="Bitcoin price prediction",
        expected_keywords=["bitcoin", "price"],
        expected_category="Crypto",
        description="Crypto market - should find Bitcoin price-related markets"
    ),
    TestCase(
        query="NBA championship winner",
        expected_keywords=["nba", "championship", "winner"],
        expected_category="Sports",
        description="Sports betting - should find NBA championship markets"
    ),
    TestCase(
        query="Federal Reserve interest rates",
        expected_keywords=["federal", "reserve", "interest", "rates", "fed"],
        description="Economic policy - should find Fed rate markets"
    ),
    TestCase(
        query="Nuclear weapon detonation",
        expected_keywords=["nuclear", "weapon", "detonation"],
        description="Geopolitical risk - should find nuclear weapon markets"
    ),
    TestCase(
        query="Tesla stock price",
        expected_keywords=["tesla", "stock", "price"],
        expected_category="Tech",
        description="Stock prediction - should find Tesla-related markets"
    ),
    TestCase(
        query="Russia Ukraine war",
        expected_keywords=["russia", "ukraine", "war"],
        description="Geopolitical - should find Russia-Ukraine conflict markets"
    ),
    TestCase(
        query="AI artificial intelligence breakthrough",
        expected_keywords=["ai", "artificial", "intelligence"],
        expected_category="Tech",
        description="Tech prediction - should find AI-related markets"
    )
]

def search_markets(query: str, limit: int = 10) -> Dict[str, Any]:
    """Search markets using the API"""
    try:
        params = {"q": query, "limit": limit}
        response = requests.get(f"{BASE_URL}/markets/search", params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Search failed for '{query}': {e}")
        return {"markets": [], "total_count": 0, "query": query}

def evaluate_relevance(market: Dict[str, Any], expected_keywords: List[str], expected_category: str = None) -> Tuple[float, str]:
    """
    Evaluate how well a market matches the expected criteria
    Returns (score, explanation)
    """
    title = market.get('title', '').lower()
    category = market.get('category', '').lower()
    
    score = 0.0
    explanations = []
    
    # Check keyword matching
    keyword_matches = 0
    for keyword in expected_keywords:
        if keyword.lower() in title:
            keyword_matches += 1
            explanations.append(f"✓ '{keyword}' found in title")
        else:
            explanations.append(f"✗ '{keyword}' missing from title")
    
    keyword_score = keyword_matches / len(expected_keywords)
    score += keyword_score * 0.7  # 70% weight for keywords
    
    # Check category matching
    if expected_category:
        if expected_category.lower() in category:
            score += 0.2  # 20% weight for category
            explanations.append(f"✓ Category '{expected_category}' matches")
        else:
            explanations.append(f"✗ Expected category '{expected_category}', got '{category}'")
    
    # Relevance score from API
    api_score = market.get('relevance_score', 0.0)
    score += api_score * 0.1  # 10% weight for API score
    explanations.append(f"API relevance: {api_score:.2f}")
    
    explanation = " | ".join(explanations)
    return score, explanation

def test_market_matching():
    """Run comprehensive market matching tests"""
    print("🎯 Market Matching Precision Test")
    print("=" * 60)
    
    total_tests = len(TEST_CASES)
    perfect_matches = 0
    good_matches = 0
    
    results = []
    
    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"\n📋 Test {i}/{total_tests}: {test_case.description}")
        print(f"🔍 Query: '{test_case.query}'")
        
        # Search for markets
        search_result = search_markets(test_case.query, limit=5)
        markets = search_result.get('markets', [])
        
        if not markets:
            print("❌ No markets found!")
            results.append({
                'test_case': test_case,
                'success': False,
                'top_score': 0.0,
                'issue': 'No markets found'
            })
            continue
        
        # Evaluate top 3 results
        print(f"📊 Found {len(markets)} markets:")
        
        top_scores = []
        for j, market in enumerate(markets[:3], 1):
            eval_score, explanation = evaluate_relevance(
                market, test_case.expected_keywords, test_case.expected_category
            )
            top_scores.append(eval_score)
            
            status = "🥇" if j == 1 else "🥈" if j == 2 else "🥉"
            print(f"  {status} Rank {j}: {market['title'][:50]}...")
            print(f"     API Score: {market['relevance_score']:.2f} | Eval Score: {eval_score:.2f}")
            print(f"     {explanation}")
        
        # Determine success
        top_score = top_scores[0] if top_scores else 0.0
        is_perfect = top_score >= 0.8
        is_good = top_score >= 0.6
        
        if is_perfect:
            perfect_matches += 1
            print("✅ PERFECT MATCH - Top result highly relevant!")
        elif is_good:
            good_matches += 1
            print("⚠️  GOOD MATCH - Top result somewhat relevant")
        else:
            print("❌ POOR MATCH - Top result not very relevant")
        
        results.append({
            'test_case': test_case,
            'success': is_perfect,
            'top_score': top_score,
            'markets_found': len(markets),
            'top_market': markets[0] if markets else None
        })
    
    # Summary
    print(f"\n🏆 FINAL RESULTS")
    print("=" * 60)
    print(f"Perfect Matches (≥80%): {perfect_matches}/{total_tests} ({perfect_matches/total_tests*100:.1f}%)")
    print(f"Good Matches (≥60%):    {good_matches}/{total_tests} ({good_matches/total_tests*100:.1f}%)")
    print(f"Poor Matches (<60%):    {total_tests - perfect_matches - good_matches}/{total_tests}")
    
    # Recommendations
    print(f"\n🔧 ALGORITHM IMPROVEMENT RECOMMENDATIONS:")
    
    poor_performers = [r for r in results if not r['success'] and r['top_score'] < 0.6]
    if poor_performers:
        print(f"❌ {len(poor_performers)} queries performed poorly:")
        for result in poor_performers:
            print(f"   • '{result['test_case'].query}' - Score: {result['top_score']:.2f}")
    
    if perfect_matches < total_tests * 0.8:  # Less than 80% perfect
        print(f"🎯 Suggested improvements:")
        print(f"   • Increase weight for exact keyword matching")
        print(f"   • Add semantic similarity using embeddings")
        print(f"   • Improve category mapping and weighting")
        print(f"   • Consider query intent classification")
        print(f"   • Add query preprocessing (stemming, synonyms)")
    
    return results

def suggest_algorithm_improvements(results: List[Dict]) -> None:
    """Analyze results and suggest specific algorithm improvements"""
    print(f"\n🧠 DETAILED ALGORITHM ANALYSIS:")
    print("=" * 60)
    
    # Analyze failure patterns
    failures = [r for r in results if not r['success']]
    
    if failures:
        print(f"📊 Failure Analysis ({len(failures)} cases):")
        
        # Check if it's a keyword matching issue
        keyword_issues = 0
        category_issues = 0
        
        for failure in failures:
            test_case = failure['test_case']
            top_market = failure.get('top_market', {})
            
            if top_market:
                title = top_market.get('title', '').lower()
                category = top_market.get('category', '').lower()
                
                # Check keyword coverage
                keyword_matches = sum(1 for kw in test_case.expected_keywords if kw.lower() in title)
                if keyword_matches < len(test_case.expected_keywords) * 0.5:
                    keyword_issues += 1
                
                # Check category matching
                if test_case.expected_category and test_case.expected_category.lower() not in category:
                    category_issues += 1
        
        print(f"   • Keyword matching issues: {keyword_issues}/{len(failures)}")
        print(f"   • Category matching issues: {category_issues}/{len(failures)}")
        
        print(f"\n💡 Specific Recommendations:")
        if keyword_issues > len(failures) * 0.5:
            print(f"   1. 🔍 Improve keyword matching:")
            print(f"      - Add synonym matching (Trump → Donald Trump)")
            print(f"      - Add stemming (election → elections)")
            print(f"      - Increase exact phrase matching weight")
        
        if category_issues > len(failures) * 0.3:
            print(f"   2. 📂 Improve category matching:")
            print(f"      - Map query topics to category preferences")
            print(f"      - Increase category bonus weight")
        
        print(f"   3. 🎯 Consider adding:")
        print(f"      - Query intent classification")
        print(f"      - Semantic embeddings for similarity")
        print(f"      - Time-based relevance (recent events)")

if __name__ == "__main__":
    # Test the API is accessible
    try:
        health_response = requests.get(f"{BASE_URL}/health", timeout=5)
        health_response.raise_for_status()
        print(f"✅ API accessible at {BASE_URL}")
    except:
        print(f"❌ Cannot access API at {BASE_URL}")
        exit(1)
    
    # Run the tests
    results = test_market_matching()
    suggest_algorithm_improvements(results)
    
    print(f"\n🎉 Test complete! Use results to tune the market matching algorithm.")
    print(f"📝 Next steps: Adjust weights in api/main.py calculate_market_relevance() function") 