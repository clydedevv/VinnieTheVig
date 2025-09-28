#!/usr/bin/env python3
"""
Enhanced Internal Testing Script for AIGG Response Quality Improvement
Focus on testing different query types and improving response quality
"""

import sys
import os
import json
import time
import requests
from datetime import datetime
from typing import Dict, List, Any

# Add paths for imports
sys.path.append('src')
sys.path.append('.')

# Test different query patterns and scenarios
TEST_SCENARIOS = {
    "crypto_predictions": [
        "Will Bitcoin reach $150K by 2025?",
        "Ethereum price predictions for 2025",
        "Will Solana outperform Bitcoin this year?",
        "Cryptocurrency market predictions",
    ],
    "political_events": [
        "Trump election predictions 2024",
        "Will Biden run for president again?", 
        "US election outcomes 2024",
        "Political betting odds Trump vs Biden",
    ],
    "ai_technology": [
        "Will AI achieve AGI by 2030?",
        "ChatGPT vs GPT-5 capabilities",
        "AI safety predictions",
        "Will AI replace human jobs by 2030?",
    ],
    "sports_entertainment": [
        "Super Bowl 2025 predictions",
        "NBA championship odds",
        "World Cup 2026 predictions",
        "Olympics 2028 betting odds",
    ],
    "economic_markets": [
        "Stock market predictions 2025",
        "Will there be a recession in 2025?",
        "Interest rate predictions",
        "Inflation forecasts 2025",
    ],
    "vague_ambiguous": [
        "What will happen?",
        "Future predictions",
        "Market trends",
        "Investment advice",
    ]
}

class AIGGResponseTester:
    def __init__(self):
        self.api_base_url = "http://localhost:8003"
        self.results = []
        
    def test_twitter_api_response(self, query: str, user_id: str = "test_user") -> Dict[str, Any]:
        """Test a single query through the Twitter API"""
        try:
            start_time = time.time()
            
            # Make API request
            response = requests.post(
                f"{self.api_base_url}/analyze",
                json={
                    "query": query,
                    "user_id": user_id,
                    "user_handle": f"test_{user_id}"
                },
                timeout=30
            )
            
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                result["api_processing_time"] = processing_time
                return result
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "api_processing_time": processing_time
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "api_processing_time": time.time() - start_time
            }
    
    def analyze_response_quality(self, query: str, response: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the quality of a response"""
        analysis = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "success": response.get("success", False),
            "processing_time": response.get("processing_time", 0),
            "api_processing_time": response.get("api_processing_time", 0),
        }
        
        if response.get("success"):
            tweet_text = response.get("tweet_text", "")
            market_title = response.get("market_title", "")
            analysis_text = response.get("analysis", "")
            
            # Quality metrics
            analysis.update({
                "tweet_length": len(tweet_text),
                "tweet_within_limits": len(tweet_text) <= 280,
                "has_market_match": bool(market_title),
                "market_title": market_title,
                "has_analysis": bool(analysis_text),
                "analysis_length": len(analysis_text),
                "has_url": "polymarket.com" in tweet_text,
                "confidence": response.get("confidence", 0),
                "recommendation": response.get("recommendation", ""),
                "url": response.get("polymarket_url", ""),
            })
            
            # Content quality assessment
            analysis["quality_score"] = self.calculate_quality_score(response)
            analysis["issues"] = self.identify_issues(response)
            analysis["suggestions"] = self.generate_suggestions(query, response)
            
        else:
            analysis.update({
                "error": response.get("error", "Unknown error"),
                "error_message": response.get("error_message", ""),
                "quality_score": 0,
                "issues": ["Failed to generate response"],
                "suggestions": ["Check API connectivity and error handling"]
            })
            
        return analysis
    
    def calculate_quality_score(self, response: Dict[str, Any]) -> float:
        """Calculate a quality score from 0-100"""
        score = 0
        
        # Basic functionality (40 points)
        if response.get("success"): score += 10
        if response.get("market_title"): score += 10
        if response.get("analysis"): score += 10
        if response.get("polymarket_url"): score += 10
        
        # Content quality (30 points)
        tweet_text = response.get("tweet_text", "")
        if len(tweet_text) > 50: score += 5  # Sufficient content
        if len(tweet_text) <= 280: score += 5  # Twitter limit
        
        analysis_text = response.get("analysis", "")
        if len(analysis_text) > 100: score += 10  # Detailed analysis
        if "%" in analysis_text or "probability" in analysis_text.lower(): score += 5  # Quantitative
        if any(word in analysis_text.lower() for word in ["because", "due to", "since", "as"]): score += 5  # Reasoning
        
        # Performance (20 points)
        processing_time = response.get("processing_time", 0)
        if processing_time < 5: score += 10
        elif processing_time < 10: score += 5
        
        confidence = response.get("confidence", 0)
        if confidence > 0.7: score += 10
        elif confidence > 0.5: score += 5
        
        # Formatting (10 points)
        if "🔗" in tweet_text or "📊" in tweet_text or "💡" in tweet_text: score += 5  # Emojis
        if response.get("recommendation") in ["BUY", "SELL", "HOLD"]: score += 5  # Clear recommendation
        
        return min(score, 100)
    
    def identify_issues(self, response: Dict[str, Any]) -> List[str]:
        """Identify potential issues with the response"""
        issues = []
        
        tweet_text = response.get("tweet_text", "")
        if len(tweet_text) > 280:
            issues.append("Tweet exceeds 280 character limit")
        
        if len(tweet_text) < 50:
            issues.append("Tweet is too short, may lack information")
        
        if not response.get("market_title"):
            issues.append("No market match found")
        
        if not response.get("analysis"):
            issues.append("No analysis provided")
        
        if response.get("processing_time", 0) > 15:
            issues.append("Slow processing time (>15 seconds)")
        
        if response.get("confidence", 0) < 0.5:
            issues.append("Low confidence in analysis")
        
        if "polymarket.com" not in tweet_text:
            issues.append("No Polymarket URL in tweet")
        
        analysis_text = response.get("analysis", "")
        if analysis_text and len(analysis_text) < 100:
            issues.append("Analysis is too brief")
        
        return issues
    
    def generate_suggestions(self, query: str, response: Dict[str, Any]) -> List[str]:
        """Generate suggestions for improvement"""
        suggestions = []
        
        if not response.get("market_title"):
            suggestions.append("Improve market matching algorithm for query: " + query[:50])
        
        if response.get("processing_time", 0) > 10:
            suggestions.append("Optimize response time - consider caching or async processing")
        
        tweet_text = response.get("tweet_text", "")
        if len(tweet_text) > 280:
            suggestions.append("Implement better tweet text truncation")
        
        if response.get("confidence", 0) < 0.6:
            suggestions.append("Improve confidence scoring or provide uncertainty indicators")
        
        analysis_text = response.get("analysis", "")
        if analysis_text and not any(word in analysis_text.lower() for word in ["because", "due to", "since"]):
            suggestions.append("Add more reasoning and explanation to analysis")
        
        if "%" not in analysis_text and "probability" not in analysis_text.lower():
            suggestions.append("Include more quantitative analysis and probabilities")
        
        return suggestions
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive testing across all scenarios"""
        print("🧪 STARTING COMPREHENSIVE AIGG RESPONSE TESTING")
        print("=" * 80)
        
        all_results = []
        category_scores = {}
        
        for category, queries in TEST_SCENARIOS.items():
            print(f"\n📊 Testing Category: {category.upper()}")
            print("-" * 50)
            
            category_results = []
            
            for i, query in enumerate(queries):
                print(f"  {i+1}. Testing: '{query}'")
                
                # Test the query
                response = self.test_twitter_api_response(query, f"test_{category}_{i}")
                analysis = self.analyze_response_quality(query, response)
                
                category_results.append(analysis)
                all_results.append(analysis)
                
                # Quick status
                status = "✅" if analysis["success"] else "❌"
                quality = analysis.get("quality_score", 0)
                time_taken = analysis.get("processing_time", 0)
                
                print(f"     {status} Quality: {quality:.1f}/100 | Time: {time_taken:.1f}s")
                
                if analysis.get("issues"):
                    print(f"     ⚠️  Issues: {len(analysis['issues'])}")
                
                # Brief pause between requests
                time.sleep(1)
            
            # Calculate category average
            category_scores[category] = {
                "avg_quality": sum(r.get("quality_score", 0) for r in category_results) / len(category_results),
                "success_rate": sum(1 for r in category_results if r["success"]) / len(category_results),
                "avg_time": sum(r.get("processing_time", 0) for r in category_results) / len(category_results),
                "total_tests": len(category_results)
            }
            
            print(f"  📈 Category Summary:")
            print(f"     Average Quality: {category_scores[category]['avg_quality']:.1f}/100")
            print(f"     Success Rate: {category_scores[category]['success_rate']*100:.1f}%")
            print(f"     Average Time: {category_scores[category]['avg_time']:.1f}s")
        
        # Generate overall report
        overall_report = self.generate_overall_report(all_results, category_scores)
        
        # Save detailed results
        self.save_results(all_results, overall_report)
        
        return overall_report
    
    def generate_overall_report(self, all_results: List[Dict], category_scores: Dict) -> Dict[str, Any]:
        """Generate overall performance report"""
        successful_results = [r for r in all_results if r["success"]]
        
        if not successful_results:
            return {
                "overall_quality": 0,
                "success_rate": 0,
                "avg_processing_time": 0,
                "total_tests": len(all_results),
                "major_issues": ["No successful responses generated"],
                "recommendations": ["Check system connectivity and API functionality"]
            }
        
        report = {
            "overall_quality": sum(r.get("quality_score", 0) for r in successful_results) / len(successful_results),
            "success_rate": len(successful_results) / len(all_results),
            "avg_processing_time": sum(r.get("processing_time", 0) for r in successful_results) / len(successful_results),
            "total_tests": len(all_results),
            "successful_tests": len(successful_results),
            "category_breakdown": category_scores,
        }
        
        # Identify major issues
        all_issues = []
        for result in all_results:
            all_issues.extend(result.get("issues", []))
        
        issue_counts = {}
        for issue in all_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1
        
        report["major_issues"] = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Generate recommendations
        recommendations = []
        if report["overall_quality"] < 70:
            recommendations.append("Overall quality needs improvement - focus on analysis depth and accuracy")
        if report["success_rate"] < 0.9:
            recommendations.append("Improve market matching reliability")
        if report["avg_processing_time"] > 10:
            recommendations.append("Optimize response time performance")
        
        # Category-specific recommendations
        for category, scores in category_scores.items():
            if scores["avg_quality"] < 60:
                recommendations.append(f"Improve {category} category responses - low quality score")
        
        report["recommendations"] = recommendations
        
        return report
    
    def save_results(self, all_results: List[Dict], overall_report: Dict):
        """Save test results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed results
        with open(f"test_results_detailed_{timestamp}.json", "w") as f:
            json.dump(all_results, f, indent=2)
        
        # Save summary report
        with open(f"test_results_summary_{timestamp}.json", "w") as f:
            json.dump(overall_report, f, indent=2)
        
        print(f"\n💾 Results saved:")
        print(f"   - Detailed: test_results_detailed_{timestamp}.json")
        print(f"   - Summary: test_results_summary_{timestamp}.json")
    
    def print_final_report(self, report: Dict[str, Any]):
        """Print comprehensive final report"""
        print("\n" + "=" * 80)
        print("📋 FINAL AIGG RESPONSE QUALITY REPORT")
        print("=" * 80)
        
        print(f"📊 Overall Performance:")
        print(f"   Quality Score: {report['overall_quality']:.1f}/100")
        print(f"   Success Rate: {report['success_rate']*100:.1f}%")
        print(f"   Avg Response Time: {report['avg_processing_time']:.1f}s")
        print(f"   Total Tests: {report['total_tests']}")
        
        print(f"\n📈 Category Breakdown:")
        for category, scores in report['category_breakdown'].items():
            print(f"   {category.replace('_', ' ').title()}:")
            print(f"     Quality: {scores['avg_quality']:.1f}/100")
            print(f"     Success: {scores['success_rate']*100:.1f}%")
            print(f"     Time: {scores['avg_time']:.1f}s")
        
        print(f"\n⚠️  Major Issues:")
        for issue, count in report['major_issues']:
            print(f"   - {issue} ({count} times)")
        
        print(f"\n💡 Recommendations:")
        for rec in report['recommendations']:
            print(f"   - {rec}")
        
        # Performance assessment
        if report['overall_quality'] >= 85:
            print(f"\n🎉 EXCELLENT: System is performing very well!")
        elif report['overall_quality'] >= 70:
            print(f"\n✅ GOOD: System is performing well with room for improvement")
        elif report['overall_quality'] >= 50:
            print(f"\n⚠️  NEEDS WORK: System needs significant improvements")
        else:
            print(f"\n❌ POOR: System requires major fixes")
        
        print("=" * 80)

def main():
    """Main testing function"""
    tester = AIGGResponseTester()
    
    try:
        # Run comprehensive testing
        overall_report = tester.run_comprehensive_test()
        
        # Print final report
        tester.print_final_report(overall_report)
        
        print("\n🎯 Testing complete! Check the generated JSON files for detailed results.")
        
    except KeyboardInterrupt:
        print("\n⚠️  Testing interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Testing failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 