#!/usr/bin/env python3
"""
Standalone Market Matching Tests - No External Dependencies
Tests the market matching algorithm logic directly
"""
import re
from typing import Dict, Any, List
from datetime import datetime


def levenshtein_ratio(s1: str, s2: str) -> float:
    """Calculate Levenshtein similarity ratio between two strings"""
    if len(s1) < len(s2):
        return levenshtein_ratio(s2, s1)

    if len(s2) == 0:
        return 0.0

    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    max_len = max(len(s1), len(s2))
    return 1.0 - (previous_row[-1] / max_len)


def calculate_market_relevance(query: str, market: Dict[str, Any]) -> float:
    """Calculate relevance score for a market given a query - ENHANCED WITH DATE CONTEXT"""
    query_lower = query.lower().strip()
    title_lower = (market.get('title') or '').lower()
    category_lower = (market.get('category') or '').lower()
    
    relevance_score = 0.0
    
    # Parse end_date for time-based scoring
    end_date = market.get('end_date')
    market_month = None
    market_year = None
    if end_date:
        try:
            if isinstance(end_date, str):
                # Handle ISO format
                parsed_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                market_month = parsed_date.month
                market_year = parsed_date.year
            else:
                market_month = end_date.month
                market_year = end_date.year
        except:
            pass
    
    # 1. EXACT PHRASE MATCHING (highest priority)
    if query_lower in title_lower:
        relevance_score += 1.0
    
    # 1b. PHRASE-LEVEL MATCHING (new)
    # Check for important multi-word phrases
    important_phrases = [
        'federal reserve', 'interest rate', 'interest rates',
        'rate cut', 'rate cuts', 'rate hike',
        'champions league', 'premier league', 'nba championship',
        'this year', 'by june', 'by end of', 'end of year'
    ]
    
    for phrase in important_phrases:
        if phrase in query_lower and phrase in title_lower:
            relevance_score += 0.5
    
    # 2. INDIVIDUAL KEYWORD MATCHING
    query_terms = set(re.findall(r'\b\w+\b', query_lower))
    title_terms = set(re.findall(r'\b\w+\b', title_lower))
    
    if query_terms and title_terms:
        exact_matches = query_terms.intersection(title_terms)
        exact_match_ratio = len(exact_matches) / len(query_terms)
        relevance_score += exact_match_ratio * 0.8
        
        # Bonus for multiple keyword matches
        if len(exact_matches) >= 2:
            relevance_score += 0.3
    
    # 3. TIME CONTEXT AWARENESS (NEW - HIGH PRIORITY FOR DATE-SENSITIVE QUERIES)
    time_context_bonus = 0.0
    
    # Check for time-related keywords in query
    year_2025_refs = ['2025', 'this year', 'by end of year', 'year end', 'december', 'end of the year']
    near_term_refs = ['june', 'july', 'august', 'september', 'this month', 'next month', 'soon']
    
    has_year_context = any(ref in query_lower for ref in year_2025_refs)
    has_near_term_context = any(ref in query_lower for ref in near_term_refs)
    
    if market_month and market_year == 2025:
        if has_year_context and not has_near_term_context:
            # Query is asking about "this year" - prefer markets ending later in 2025
            if market_month >= 11:  # Nov-Dec markets
                time_context_bonus += 0.4  # Strong bonus for end-of-year markets
            elif market_month >= 9:  # Sep-Oct markets  
                time_context_bonus += 0.2  # Medium bonus
            elif market_month >= 7:  # Jul-Aug markets
                time_context_bonus += 0.1  # Small bonus
            else:  # Jan-Jun markets
                time_context_bonus -= 0.2  # Penalty for early-year markets when asking about "this year"
        
        elif has_near_term_context:
            # Query is asking about near-term - prefer markets ending soon
            if market_month <= 7:  # Jan-Jul markets
                time_context_bonus += 0.3
            elif market_month <= 9:  # Aug-Sep markets
                time_context_bonus += 0.1
            else:  # Oct-Dec markets
                time_context_bonus -= 0.1
    
    relevance_score += time_context_bonus
    
    # 4. SEMANTIC/SYNONYM MATCHING
    synonym_map = {
        'trump': ['donald'],
        'donald': ['trump'],
        'bitcoin': ['btc', 'crypto'],
        'btc': ['bitcoin', 'crypto'],
        'crypto': ['bitcoin', 'btc', 'cryptocurrency'],
        'election': ['voting', 'vote', 'elections'],
        'championship': ['finals', 'champion', 'winner'],
        'price': ['value', 'cost', 'hit', 'reach', 'reaching'],
        'ai': ['artificial intelligence'],
        'artificial intelligence': ['ai'],
        'federal reserve': ['fed', 'fomc', 'federal', 'reserve'],
        'fed': ['federal reserve', 'fomc', 'federal', 'reserve'],
        'interest': ['rate', 'rates'],
        'rate': ['interest', 'rates'],
        'rates': ['interest', 'rate'],
        'nuclear': ['atomic'],
        'war': ['conflict', 'fighting'],
        'this year': ['2025', 'end of year', 'year end'],
        'year': ['2025'],
        '200k': ['200000', '$200k', '$200,000'],
        '120k': ['120000', '$120k', '$120,000'],
        '150k': ['150000', '$150k', '$150,000']
    }
    
    synonym_bonus = 0.0
    for term in query_terms:
        if term in synonym_map:
            for synonym in synonym_map[term]:
                if synonym in title_lower:
                    synonym_bonus += 0.2
    
    relevance_score += min(synonym_bonus, 0.4)
    
    # 5. CATEGORY MATCHING
    category_map = {
        'trump': ['us-current-affairs', 'politics'],
        'election': ['us-current-affairs', 'politics'],
        'bitcoin': ['crypto'],
        'nba': ['sports', 'nba'],
        'basketball': ['sports', 'nba'],
        'tesla': ['tech', 'stocks'],
        'stock': ['tech', 'finance'],
        'federal reserve': ['economics', 'finance'],
        'nuclear': ['geopolitics', 'military'],
        'ai': ['tech', 'artificial intelligence'],
        'russia': ['geopolitics'],
        'ukraine': ['geopolitics']
    }
    
    category_bonus = 0.0
    for term in query_terms:
        if term in category_map:
            for expected_cat in category_map[term]:
                if expected_cat.lower() in category_lower:
                    category_bonus += 0.3
    
    relevance_score += min(category_bonus, 0.4)
    
    # 6. STRING SIMILARITY (refined)
    title_similarity = levenshtein_ratio(query_lower, title_lower)
    if title_similarity > 0.3:
        relevance_score += title_similarity * 0.3
    
    # 7. QUERY LENGTH CONSIDERATION
    if len(query_terms) <= 2:
        if exact_match_ratio < 0.5:
            relevance_score *= 0.7
    
    # 8. TITLE LENGTH CONSIDERATION
    title_word_count = len(title_terms)
    if title_word_count < 10:
        relevance_score += 0.1
    
    # 9. ACTIVE MARKET BONUS
    if market.get('active'):
        relevance_score += 0.05
    
    return min(relevance_score, 1.0)


def run_market_matching_tests():
    """Run tests and print results"""
    # Real Polymarket markets
    real_markets = [
        # Sports Markets
        {
            "market_id": "champ-league-2025",
            "title": "Which team will win the 2024-25 UEFA Champions League?",
            "category": "Sports",
            "end_date": "2025-06-01T00:00:00Z",
            "active": True,
            "market_slug": "champions-league-2025-winner"
        },
        {
            "market_id": "nba-champ-2025",
            "title": "Which team will win the 2024-25 NBA Championship?",
            "category": "NBA",
            "end_date": "2025-06-15T00:00:00Z",
            "active": True,
            "market_slug": "nba-championship-2025"
        },
        {
            "market_id": "premier-league-2025",
            "title": "Which club will win the 2024-25 Premier League?",
            "category": "Sports",
            "end_date": "2025-05-25T00:00:00Z",
            "active": True,
            "market_slug": "premier-league-2025-winner"
        },
        
        # Bitcoin/Crypto Markets
        {
            "market_id": "btc-120k-2025",
            "title": "Will Bitcoin hit $120,000 in 2025?",
            "category": "Crypto",
            "end_date": "2025-12-31T23:59:59Z",
            "active": True,
            "market_slug": "bitcoin-120k-2025"
        },
        {
            "market_id": "btc-200k-2025",
            "title": "Will Bitcoin reach $200,000 by end of 2025?",
            "category": "Crypto",
            "end_date": "2025-12-31T23:59:59Z",
            "active": True,
            "market_slug": "bitcoin-200k-eoy-2025"
        },
        {
            "market_id": "btc-150k-june",
            "title": "Will Bitcoin hit $150,000 by June 2025?",
            "category": "Crypto",
            "end_date": "2025-06-30T23:59:59Z",
            "active": True,
            "market_slug": "bitcoin-150k-june-2025"
        },
        
        # Federal Reserve Markets
        {
            "market_id": "fed-cuts-2025",
            "title": "How many times will the Fed cut rates in 2025?",
            "category": "Economics",
            "end_date": "2025-12-31T23:59:59Z",
            "active": True,
            "market_slug": "fed-rate-cuts-2025"
        },
        {
            "market_id": "fed-march-cut",
            "title": "Will the Fed cut rates at the March 2025 FOMC meeting?",
            "category": "Economics",
            "end_date": "2025-03-19T18:00:00Z",
            "active": True,
            "market_slug": "fed-march-2025-cut"
        },
        
        # Geopolitical Markets
        {
            "market_id": "ukraine-ceasefire-2025",
            "title": "Will Russia and Ukraine agree to a ceasefire in 2025?",
            "category": "Geopolitics",
            "end_date": "2025-12-31T23:59:59Z",
            "active": True,
            "market_slug": "russia-ukraine-ceasefire-2025"
        },
        {
            "market_id": "ukraine-peace-june",
            "title": "Will there be a Russia-Ukraine peace agreement by June 2025?",
            "category": "Geopolitics",
            "end_date": "2025-06-30T23:59:59Z",
            "active": True,
            "market_slug": "ukraine-peace-june-2025"
        }
    ]
    
    # Test queries
    test_queries = [
        "Bitcoin reaching $200k this year",
        "Will BTC hit 150k by June?",
        "Fed rate cut in March",
        "Ukraine Russia ceasefire",
        "NBA championship Celtics",
        "Champions League winner",
        "Bitcoin 120k 2025",
        "Federal Reserve interest rates"
    ]
    
    print("=" * 100)
    print("MARKET MATCHING TEST RESULTS")
    print("=" * 100)
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        print("-" * 80)
        
        # Calculate scores for all markets
        scores = []
        for market in real_markets:
            score = calculate_market_relevance(query, market)
            scores.append({
                "market": market,
                "score": score
            })
        
        # Sort by score
        scores.sort(key=lambda x: x["score"], reverse=True)
        
        # Print top 3 matches
        for i, result in enumerate(scores[:3], 1):
            market = result["market"]
            score = result["score"]
            print(f"{i}. [{score:.3f}] {market['title']}")
            if score > 0:
                # Explain why it scored well
                explain_score(query, market, score)
        
        if scores[0]["score"] < 0.3:
            print("⚠️  WARNING: Low confidence match - may need algorithm improvement")
    
    print("\n" + "=" * 100)
    print("ALGORITHM ANALYSIS")
    print("=" * 100)
    analyze_algorithm_performance(test_queries, real_markets)


def explain_score(query: str, market: Dict[str, Any], score: float):
    """Explain why a market scored well for a query"""
    explanations = []
    query_lower = query.lower()
    title_lower = market['title'].lower()
    
    # Check exact phrase match
    if query_lower in title_lower:
        explanations.append("exact phrase match")
    
    # Check keyword matches
    query_terms = set(re.findall(r'\b\w+\b', query_lower))
    title_terms = set(re.findall(r'\b\w+\b', title_lower))
    matches = query_terms.intersection(title_terms)
    if matches:
        explanations.append(f"keywords: {', '.join(matches)}")
    
    # Check time context
    if 'this year' in query_lower and '2025' in market.get('end_date', ''):
        end_date = datetime.fromisoformat(market['end_date'].replace('Z', '+00:00'))
        if end_date.month >= 11:
            explanations.append("end-of-year timeframe match")
    
    if explanations:
        print(f"   → {'; '.join(explanations)}")


def analyze_algorithm_performance(queries: List[str], markets: List[Dict]):
    """Analyze overall algorithm performance"""
    total_tests = len(queries)
    high_confidence = 0
    medium_confidence = 0
    low_confidence = 0
    
    for query in queries:
        scores = []
        for market in markets:
            score = calculate_market_relevance(query, market)
            scores.append(score)
        
        top_score = max(scores)
        if top_score >= 0.7:
            high_confidence += 1
        elif top_score >= 0.4:
            medium_confidence += 1
        else:
            low_confidence += 1
    
    print(f"Total queries tested: {total_tests}")
    print(f"High confidence matches (≥0.7): {high_confidence} ({high_confidence/total_tests*100:.1f}%)")
    print(f"Medium confidence matches (0.4-0.7): {medium_confidence} ({medium_confidence/total_tests*100:.1f}%)")
    print(f"Low confidence matches (<0.4): {low_confidence} ({low_confidence/total_tests*100:.1f}%)")
    
    print("\nRECOMMENDATIONS:")
    if low_confidence > total_tests * 0.2:
        print("⚠️  More than 20% of queries have low confidence - consider improving:")
        print("   - Add more synonyms and semantic understanding")
        print("   - Improve fuzzy matching for partial queries")
        print("   - Enhance category mapping")


if __name__ == "__main__":
    run_market_matching_tests()