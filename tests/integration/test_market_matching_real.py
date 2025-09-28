#!/usr/bin/env python3
"""
Real Market Matching Tests - Based on Actual Polymarket Data
Tests market matching algorithm with real-world queries and markets
"""
import unittest
from datetime import datetime
from typing import List, Dict, Any
from api.main import calculate_market_relevance
from src.flows.dspy_enhanced_aigg_flow import DSPyEnhancedAIGGFlow


class TestRealMarketMatching(unittest.TestCase):
    """Test market matching with real Polymarket examples"""
    
    def setUp(self):
        """Set up test fixtures with real market data"""
        # Real Polymarket markets based on search results
        self.real_markets = [
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
            {
                "market_id": "nba-east-2025",
                "title": "Which team will win the 2024-25 NBA Eastern Conference?",
                "category": "NBA",
                "end_date": "2025-05-30T00:00:00Z",
                "active": True,
                "market_slug": "nba-eastern-conference-2025"
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
                "market_id": "btc-70k-2025",
                "title": "Will Bitcoin fall below $70,000 in 2025?",
                "category": "Crypto",
                "end_date": "2025-12-31T23:59:59Z",
                "active": True,
                "market_slug": "bitcoin-70k-2025"
            },
            {
                "market_id": "btc-100k-12mo",
                "title": "Will Bitcoin reach $100,000 in the next 12 months?",
                "category": "Crypto",
                "end_date": "2026-01-27T00:00:00Z",
                "active": True,
                "market_slug": "bitcoin-100k-12-months"
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
                "market_id": "fed-hike-2025",
                "title": "Will the Federal Reserve raise interest rates in 2025?",
                "category": "Finance",
                "end_date": "2025-12-31T23:59:59Z",
                "active": True,
                "market_slug": "fed-rate-hike-2025"
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
                "market_id": "putin-exit-2025",
                "title": "Will Vladimir Putin exit the presidency by end of 2025?",
                "category": "Geopolitics",
                "end_date": "2025-12-31T23:59:59Z",
                "active": True,
                "market_slug": "putin-exit-2025"
            },
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
            },
            
            # Election Markets
            {
                "market_id": "nyc-mayor-2025",
                "title": "Who will win the 2025 NYC mayoral election?",
                "category": "Politics",
                "end_date": "2025-11-04T23:59:59Z",
                "active": True,
                "market_slug": "nyc-mayor-2025"
            },
            {
                "market_id": "irish-president-2025",
                "title": "Who will win the 2025 Irish presidential election?",
                "category": "Politics",
                "end_date": "2025-11-15T23:59:59Z",
                "active": True,
                "market_slug": "irish-president-2025"
            },
            
            # Celebrity/Legal Markets
            {
                "market_id": "epstein-docs-2025",
                "title": "Will the Epstein client list be officially released in 2025?",
                "category": "Current Affairs",
                "end_date": "2025-12-31T23:59:59Z",
                "active": True,
                "market_slug": "epstein-list-release-2025"
            },
            {
                "market_id": "diddy-conviction-2025",
                "title": "Will Sean 'Diddy' Combs be convicted of federal charges in 2025?",
                "category": "Legal",
                "end_date": "2025-12-31T23:59:59Z",
                "active": True,
                "market_slug": "diddy-conviction-2025"
            }
        ]
        
        self.flow = DSPyEnhancedAIGGFlow()
    
    def test_sports_queries(self):
        """Test sports-related queries matching to correct markets"""
        test_cases = [
            {
                "query": "Who will win Champions League?",
                "expected_market_id": "champ-league-2025",
                "reason": "Direct Champions League query should match Champions League market"
            },
            {
                "query": "NBA championship winner 2025",
                "expected_market_id": "nba-champ-2025",
                "reason": "NBA championship query should match NBA championship market"
            },
            {
                "query": "Liverpool Premier League title",
                "expected_market_id": "premier-league-2025",
                "reason": "Premier League query should match Premier League market"
            },
            {
                "query": "Celtics Eastern Conference",
                "expected_market_id": "nba-east-2025",
                "reason": "NBA Eastern Conference query should match Eastern Conference market"
            }
        ]
        
        for test in test_cases:
            with self.subTest(query=test["query"]):
                scores = self._calculate_all_scores(test["query"])
                top_market = max(scores, key=lambda x: x["score"])
                
                self.assertEqual(
                    top_market["market_id"], 
                    test["expected_market_id"],
                    f"{test['reason']}. Got {top_market['market_id']} with score {top_market['score']:.3f}"
                )
    
    def test_bitcoin_price_queries(self):
        """Test Bitcoin price queries with time context"""
        test_cases = [
            {
                "query": "Bitcoin 200k this year",
                "expected_market_id": "btc-200k-2025",
                "reason": "Bitcoin 200k this year should match end of 2025 market"
            },
            {
                "query": "Will BTC hit 150k by June?",
                "expected_market_id": "btc-150k-june",
                "reason": "Bitcoin 150k June query should match June-specific market"
            },
            {
                "query": "Bitcoin reaching $120,000 in 2025",
                "expected_market_id": "btc-120k-2025",
                "reason": "Exact price and year should match specific market"
            },
            {
                "query": "BTC 100k next 12 months",
                "expected_market_id": "btc-100k-12mo",
                "reason": "12 month timeframe should match 12-month market"
            }
        ]
        
        for test in test_cases:
            with self.subTest(query=test["query"]):
                scores = self._calculate_all_scores(test["query"])
                top_market = max(scores, key=lambda x: x["score"])
                
                self.assertEqual(
                    top_market["market_id"], 
                    test["expected_market_id"],
                    f"{test['reason']}. Got {top_market['market_id']} with score {top_market['score']:.3f}"
                )
    
    def test_federal_reserve_queries(self):
        """Test Federal Reserve and interest rate queries"""
        test_cases = [
            {
                "query": "Fed rate cuts 2025",
                "expected_market_id": "fed-cuts-2025",
                "reason": "Fed cuts query should match rate cuts market"
            },
            {
                "query": "Will Federal Reserve raise interest rates?",
                "expected_market_id": "fed-hike-2025",
                "reason": "Fed raise rates query should match rate hike market"
            },
            {
                "query": "March FOMC meeting rate cut",
                "expected_market_id": "fed-march-cut",
                "reason": "March FOMC query should match March-specific market"
            }
        ]
        
        for test in test_cases:
            with self.subTest(query=test["query"]):
                scores = self._calculate_all_scores(test["query"])
                top_market = max(scores, key=lambda x: x["score"])
                
                self.assertEqual(
                    top_market["market_id"], 
                    test["expected_market_id"],
                    f"{test['reason']}. Got {top_market['market_id']} with score {top_market['score']:.3f}"
                )
    
    def test_geopolitical_queries(self):
        """Test geopolitical event queries"""
        test_cases = [
            {
                "query": "Russia Ukraine ceasefire 2025",
                "expected_market_id": "ukraine-ceasefire-2025",
                "reason": "Ceasefire query should match ceasefire market"
            },
            {
                "query": "Ukraine peace agreement by June",
                "expected_market_id": "ukraine-peace-june",
                "reason": "Peace by June query should match June-specific market"
            },
            {
                "query": "Putin presidency exit",
                "expected_market_id": "putin-exit-2025",
                "reason": "Putin exit query should match Putin presidency market"
            }
        ]
        
        for test in test_cases:
            with self.subTest(query=test["query"]):
                scores = self._calculate_all_scores(test["query"])
                top_market = max(scores, key=lambda x: x["score"])
                
                self.assertEqual(
                    top_market["market_id"], 
                    test["expected_market_id"],
                    f"{test['reason']}. Got {top_market['market_id']} with score {top_market['score']:.3f}"
                )
    
    def test_ambiguous_queries(self):
        """Test handling of ambiguous queries"""
        test_cases = [
            {
                "query": "bitcoin",
                "acceptable_markets": ["btc-120k-2025", "btc-200k-2025", "btc-100k-12mo", "btc-150k-june"],
                "reason": "Single word 'bitcoin' could match multiple Bitcoin markets"
            },
            {
                "query": "election",
                "acceptable_markets": ["nyc-mayor-2025", "irish-president-2025"],
                "reason": "Generic 'election' could match multiple election markets"
            },
            {
                "query": "2025",
                "min_markets": 5,
                "reason": "Year-only query should match multiple 2025 markets"
            }
        ]
        
        for test in test_cases:
            with self.subTest(query=test["query"]):
                scores = self._calculate_all_scores(test["query"])
                relevant_scores = [s for s in scores if s["score"] > 0.1]
                
                if "acceptable_markets" in test:
                    top_market = max(scores, key=lambda x: x["score"])
                    self.assertIn(
                        top_market["market_id"],
                        test["acceptable_markets"],
                        f"{test['reason']}. Got {top_market['market_id']}"
                    )
                elif "min_markets" in test:
                    self.assertGreaterEqual(
                        len(relevant_scores),
                        test["min_markets"],
                        f"{test['reason']}. Found only {len(relevant_scores)} relevant markets"
                    )
    
    def test_dspy_query_preprocessing(self):
        """Test DSPy query understanding and preprocessing"""
        test_queries = [
            ("Will Bitcoin hit 200k?", "bitcoin", "200k"),
            ("Fed interest rate decision", "fed", "interest rate"),
            ("Who wins NBA championship", "nba", "championship"),
            ("Russia Ukraine war end", "russia ukraine", "war")
        ]
        
        for query, expected_term1, expected_term2 in test_queries:
            with self.subTest(query=query):
                search_terms, topic, entities = self.flow.dspy_understand_query(query)
                
                # Check that key terms are extracted
                self.assertTrue(
                    expected_term1.lower() in search_terms.lower() or 
                    expected_term1.lower() in topic.lower() or
                    expected_term1.lower() in entities.lower(),
                    f"Expected '{expected_term1}' in DSPy output for query: {query}"
                )
    
    def test_relevance_score_ordering(self):
        """Test that relevance scores properly order results"""
        # Test that exact matches score higher than partial matches
        exact_query = "Will Bitcoin hit $120,000 in 2025?"
        scores = self._calculate_all_scores(exact_query)
        
        # Find the exact match market
        exact_match = next(s for s in scores if s["market_id"] == "btc-120k-2025")
        other_btc_markets = [s for s in scores if "btc" in s["market_id"] and s["market_id"] != "btc-120k-2025"]
        
        # Exact match should score higher than other Bitcoin markets
        for other in other_btc_markets:
            self.assertGreater(
                exact_match["score"],
                other["score"],
                f"Exact match should score higher than {other['market_id']}"
            )
    
    def test_time_sensitive_scoring(self):
        """Test that time context affects scoring appropriately"""
        # Query about "this year" should prefer end-of-year markets
        year_query = "Bitcoin 200k this year"
        scores = self._calculate_all_scores(year_query)
        
        eoy_market = next(s for s in scores if s["market_id"] == "btc-200k-2025")
        june_market = next(s for s in scores if s["market_id"] == "btc-150k-june")
        
        self.assertGreater(
            eoy_market["score"],
            june_market["score"],
            "End-of-year market should score higher for 'this year' query"
        )
        
        # Query about "by June" should prefer June markets
        june_query = "Bitcoin price by June"
        scores = self._calculate_all_scores(june_query)
        
        june_market = next(s for s in scores if s["market_id"] == "btc-150k-june")
        eoy_market = next(s for s in scores if s["market_id"] == "btc-200k-2025")
        
        self.assertGreater(
            june_market["score"],
            eoy_market["score"],
            "June market should score higher for 'by June' query"
        )
    
    def _calculate_all_scores(self, query: str) -> List[Dict[str, Any]]:
        """Calculate relevance scores for all markets"""
        scores = []
        for market in self.real_markets:
            score = calculate_market_relevance(query, market)
            scores.append({
                "market_id": market["market_id"],
                "title": market["title"],
                "score": score
            })
        return sorted(scores, key=lambda x: x["score"], reverse=True)
    
    def test_print_top_matches(self):
        """Utility test to print top matches for various queries"""
        test_queries = [
            "Bitcoin reaching $200k this year",
            "Fed rate cut in March",
            "Ukraine Russia ceasefire",
            "NBA championship Celtics",
            "Epstein documents release"
        ]
        
        print("\n" + "="*80)
        print("TOP MARKET MATCHES FOR COMMON QUERIES")
        print("="*80)
        
        for query in test_queries:
            scores = self._calculate_all_scores(query)
            print(f"\nQuery: '{query}'")
            print("-" * 50)
            
            for i, result in enumerate(scores[:3], 1):
                print(f"{i}. [{result['score']:.3f}] {result['title'][:60]}...")


if __name__ == "__main__":
    unittest.main(verbosity=2)