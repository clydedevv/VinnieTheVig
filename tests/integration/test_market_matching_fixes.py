#!/usr/bin/env python3
"""
Comprehensive Test Suite for Market Matching Fixes
Tests the three critical issues:
1. Broken Market Links: URL generation creating non-existent market pages
2. Wrong Market Matching: Focusing on "June 2025" instead of "this year"  
3. Need Internal Testing: Before going fully live
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

API_BASE = "http://localhost:8001"

class MarketMatchingTester:
    """Comprehensive testing for market matching improvements"""
    
    def __init__(self):
        self.results = []
        self.failed_tests = []
        
    def test_time_context_queries(self):
        """Test time-context aware market matching"""
        print("\n🕒 TIME CONTEXT MATCHING TESTS")
        print("=" * 60)
        
        time_tests = [
            {
                "query": "Will Bitcoin reach $150K this year?",
                "expected_preference": "december",  # Should prefer Dec 2025 over June 2025
                "description": "This year query should prefer end-of-year markets"
            },
            {
                "query": "Bitcoin $150,000 by 2025",
                "expected_preference": "december",
                "description": "2025 query should prefer latest 2025 market"
            },
            {
                "query": "Will Bitcoin hit $150K by end of year?",
                "expected_preference": "december", 
                "description": "End of year query should strongly prefer December"
            },
            {
                "query": "Bitcoin $150K in June",
                "expected_preference": "june",
                "description": "Specific month query should prefer that month"
            }
        ]
        
        for test in time_tests:
            print(f"\n📋 Test: {test['description']}")
            print(f"🔍 Query: '{test['query']}'")
            
            markets = self._search_markets(test['query'], limit=5)
            if markets:
                top_market = markets[0]
                print(f"🥇 Top Result: {top_market['title']}")
                print(f"📅 End Date: {top_market.get('end_date', 'Unknown')}")
                print(f"📊 Relevance: {top_market.get('relevance_score', 0):.3f}")
                
                # Check if preference is correct
                title_lower = top_market['title'].lower()
                expected_pref = test['expected_preference']
                
                if expected_pref in title_lower:
                    print(f"✅ CORRECT: Preferred {expected_pref} market")
                    self.results.append({'test': test['query'], 'status': 'PASS', 'issue': None})
                else:
                    print(f"❌ INCORRECT: Expected {expected_pref} preference")
                    self.results.append({'test': test['query'], 'status': 'FAIL', 'issue': f'Expected {expected_pref} preference'})
                    self.failed_tests.append(test)
                
                # Show other relevant markets for context
                if len(markets) > 1:
                    print("📋 Other matches:")
                    for i, market in enumerate(markets[1:4], 2):
                        end_date = market.get('end_date', '')[:10] if market.get('end_date') else 'Unknown'
                        print(f"   {i}. {market.get('relevance_score', 0):.3f}: {market['title'][:50]}... ({end_date})")
            else:
                print("❌ No markets found")
                self.results.append({'test': test['query'], 'status': 'FAIL', 'issue': 'No markets found'})
                self.failed_tests.append(test)

    def test_url_generation(self):
        """Test market URL generation and accessibility"""
        print("\n🔗 URL GENERATION TESTS")
        print("=" * 60)
        
        # Test specific queries that should have working URLs
        url_tests = [
            "Bitcoin $150K this year",
            "Will Trump fire his cabinet?", 
            "NBA Finals 2025 champion",
            "Nuclear war by 2025"
        ]
        
        for query in url_tests:
            print(f"\n🔍 Testing URLs for: '{query}'")
            
            markets = self._search_markets(query, limit=3)
            if markets:
                for i, market in enumerate(markets, 1):
                    title = market['title'][:50]
                    slug = market.get('market_slug', '')
                    
                    if slug:
                        url = f"https://polymarket.com/event/{slug}"
                        print(f"   {i}. {title}...")
                        print(f"      URL: {url}")
                        
                        # Test URL accessibility
                        url_status = self._test_url_accessibility(url)
                        if url_status == 200:
                            print(f"      ✅ URL accessible")
                            self.results.append({'test': f'URL for {query}', 'status': 'PASS', 'issue': None})
                        else:
                            print(f"      ❌ URL returns {url_status}")
                            self.results.append({'test': f'URL for {query}', 'status': 'FAIL', 'issue': f'URL returns {url_status}'})
                    else:
                        print(f"   {i}. {title}...")
                        print(f"      ❌ No market slug available")
                        self.results.append({'test': f'URL for {query}', 'status': 'FAIL', 'issue': 'No market slug'})
            else:
                print(f"   ❌ No markets found for query")
                self.results.append({'test': f'URL for {query}', 'status': 'FAIL', 'issue': 'No markets found'})

    def test_market_matching_precision(self):
        """Test precision of market matching for common queries"""
        print("\n🎯 MARKET MATCHING PRECISION TESTS")
        print("=" * 60)
        
        precision_tests = [
            {
                "query": "Will Trump be president in 2025?",
                "must_contain": ["trump", "president"],
                "should_not_contain": ["biden", "harris"]
            },
            {
                "query": "Bitcoin price $150,000",
                "must_contain": ["bitcoin", "150"],
                "should_not_contain": ["ethereum", "dogecoin"]
            },
            {
                "query": "NBA championship 2025",
                "must_contain": ["nba", "champion"],
                "should_not_contain": ["nfl", "baseball"]
            },
            {
                "query": "AI model GPT-5 release",
                "must_contain": ["ai", "gpt"],
                "should_not_contain": ["claude", "meta"]
            }
        ]
        
        for test in precision_tests:
            print(f"\n🔍 Query: '{test['query']}'")
            
            markets = self._search_markets(test['query'], limit=3)
            if markets:
                top_market = markets[0]
                title_lower = top_market['title'].lower()
                
                # Check must_contain requirements
                missing_required = []
                for required in test['must_contain']:
                    if required.lower() not in title_lower:
                        missing_required.append(required)
                
                # Check should_not_contain requirements  
                unwanted_found = []
                for unwanted in test['should_not_contain']:
                    if unwanted.lower() in title_lower:
                        unwanted_found.append(unwanted)
                
                print(f"🥇 Top Result: {top_market['title']}")
                print(f"📊 Relevance: {top_market.get('relevance_score', 0):.3f}")
                
                if not missing_required and not unwanted_found:
                    print(f"✅ PRECISE MATCH: Contains all required terms, no unwanted terms")
                    self.results.append({'test': test['query'], 'status': 'PASS', 'issue': None})
                else:
                    issues = []
                    if missing_required:
                        issues.append(f"Missing: {missing_required}")
                    if unwanted_found:
                        issues.append(f"Unwanted: {unwanted_found}")
                    print(f"❌ IMPRECISE: {' | '.join(issues)}")
                    self.results.append({'test': test['query'], 'status': 'FAIL', 'issue': ' | '.join(issues)})
            else:
                print(f"❌ No markets found")
                self.results.append({'test': test['query'], 'status': 'FAIL', 'issue': 'No markets found'})

    def test_edge_cases(self):
        """Test edge cases and potential failure modes"""
        print("\n⚠️  EDGE CASE TESTS")
        print("=" * 60)
        
        edge_tests = [
            "empty query: ''",
            "single word: bitcoin",
            "very long query: Will Bitcoin reach one hundred and fifty thousand dollars by the end of December 2025 according to prediction markets",
            "special characters: Bitcoin $150K by 2025!!! 🚀",
            "mixed case: BiTcOiN $150k THIS YEAR",
            "typos: Bitcoon reach 150k",
            "ambiguous: Will it happen?",
            "multiple questions: Bitcoin $150K or Ethereum $10K?"
        ]
        
        for test_desc in edge_tests:
            if ': ' in test_desc:
                test_type, query = test_desc.split(': ', 1)
                query = query.strip("'\"")
            else:
                test_type = "unknown"
                query = test_desc
            
            print(f"\n🧪 {test_type}: '{query}'")
            
            try:
                markets = self._search_markets(query, limit=1)
                if markets:
                    print(f"✅ Handled gracefully: Found {len(markets)} markets")
                    self.results.append({'test': test_desc, 'status': 'PASS', 'issue': None})
                else:
                    print(f"⚠️  No results (acceptable for edge case)")
                    self.results.append({'test': test_desc, 'status': 'PASS', 'issue': 'No results (acceptable)'})
            except Exception as e:
                print(f"❌ ERROR: {e}")
                self.results.append({'test': test_desc, 'status': 'FAIL', 'issue': f'Exception: {e}'})

    def _search_markets(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Helper to search markets via API"""
        try:
            response = requests.get(
                f"{API_BASE}/markets/search",
                params={"q": query, "limit": limit},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return data.get('markets', [])
        except Exception as e:
            print(f"   ❌ API Error: {e}")
            return []

    def _test_url_accessibility(self, url: str) -> int:
        """Test if a URL is accessible"""
        try:
            response = requests.head(url, timeout=10)
            return response.status_code
        except:
            return 0

    def generate_summary_report(self):
        """Generate final test summary report"""
        print("\n📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r['status'] == 'PASS'])
        failed_tests = len([r for r in self.results if r['status'] == 'FAIL'])
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests} ({passed_tests/total_tests*100:.1f}%)")
        print(f"❌ Failed: {failed_tests} ({failed_tests/total_tests*100:.1f}%)")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.results:
                if result['status'] == 'FAIL':
                    print(f"   • {result['test']}: {result['issue']}")
        
        if passed_tests / total_tests >= 0.8:
            print(f"\n🎉 OVERALL: EXCELLENT - System ready for production!")
        elif passed_tests / total_tests >= 0.6:
            print(f"\n⚠️  OVERALL: GOOD - Minor issues to address")
        else:
            print(f"\n🚨 OVERALL: NEEDS IMPROVEMENT - Major issues found")
        
        return {
            'total': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'pass_rate': passed_tests / total_tests,
            'failed_details': [r for r in self.results if r['status'] == 'FAIL']
        }

def main():
    """Run comprehensive test suite"""
    print("🧪 AIGG MARKET MATCHING & URL GENERATION TEST SUITE")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Testing API: {API_BASE}")
    
    # Check API health first
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is healthy and accessible")
        else:
            print(f"⚠️  API health check returned {response.status_code}")
    except Exception as e:
        print(f"❌ API not accessible: {e}")
        return
    
    tester = MarketMatchingTester()
    
    # Run all test suites
    tester.test_time_context_queries()
    tester.test_url_generation() 
    tester.test_market_matching_precision()
    tester.test_edge_cases()
    
    # Generate final report
    summary = tester.generate_summary_report()
    
    print(f"\n🏁 Testing completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return summary

if __name__ == "__main__":
    main() 