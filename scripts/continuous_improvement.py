#!/usr/bin/env python3
"""
Continuous Improvement Monitor for AIGG
Lightweight script for ongoing quality tracking and improvement suggestions
"""

import json
import time
import requests
from datetime import datetime
from typing import Dict, List
import subprocess

class AIGGContinuousMonitor:
    def __init__(self):
        self.api_url = "http://localhost:8003"
        self.quality_log = "quality_improvements.log"
        
    def quick_quality_check(self) -> Dict:
        """Run a quick quality check with key test queries"""
        test_queries = [
            "Bitcoin price predictions 2025",
            "Will AI achieve AGI by 2030?", 
            "Trump election predictions",
            "Stock market crash 2025",
        ]
        
        results = []
        total_time = 0
        
        print("🔍 Running quick quality check...")
        
        for query in test_queries:
            start_time = time.time()
            
            try:
                response = requests.post(
                    f"{self.api_url}/analyze",
                    json={"query": query, "user_id": "monitor", "user_handle": "test"},
                    timeout=20
                )
                
                processing_time = time.time() - start_time
                total_time += processing_time
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Quick quality assessment
                    analysis_length = len(result.get("analysis", ""))
                    tweet_length = len(result.get("tweet_text", ""))
                    
                    quality_score = 0
                    if result.get("success"): quality_score += 25
                    if analysis_length >= 80: quality_score += 25
                    if tweet_length <= 280: quality_score += 25  
                    if processing_time < 12: quality_score += 25
                    
                    results.append({
                        "query": query,
                        "success": result.get("success", False),
                        "processing_time": processing_time,
                        "analysis_length": analysis_length,
                        "tweet_length": tweet_length,
                        "quality_score": quality_score,
                        "confidence": result.get("confidence", 0)
                    })
                    
                    status = "✅" if quality_score >= 75 else "⚠️" if quality_score >= 50 else "❌"
                    print(f"  {status} {query[:30]}... | Score: {quality_score}/100 | Time: {processing_time:.1f}s")
                    
                else:
                    results.append({
                        "query": query,
                        "success": False,
                        "error": f"HTTP {response.status_code}",
                        "processing_time": processing_time,
                        "quality_score": 0
                    })
                    print(f"  ❌ {query[:30]}... | Error: HTTP {response.status_code}")
                    
            except Exception as e:
                results.append({
                    "query": query,
                    "success": False, 
                    "error": str(e),
                    "processing_time": time.time() - start_time,
                    "quality_score": 0
                })
                print(f"  ❌ {query[:30]}... | Error: {str(e)[:40]}")
                
            time.sleep(1)  # Brief pause between requests
        
        # Calculate summary
        avg_quality = sum(r.get("quality_score", 0) for r in results) / len(results)
        avg_time = total_time / len(results) 
        success_rate = sum(1 for r in results if r.get("success", False)) / len(results)
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "avg_quality_score": avg_quality,
            "avg_processing_time": avg_time,
            "success_rate": success_rate,
            "total_tests": len(results),
            "results": results
        }
        
        print(f"\n📊 Quick Check Summary:")
        print(f"   Quality Score: {avg_quality:.1f}/100")
        print(f"   Success Rate: {success_rate*100:.1f}%")
        print(f"   Avg Time: {avg_time:.1f}s")
        
        return summary
    
    def log_quality_metrics(self, summary: Dict):
        """Log quality metrics to file"""
        log_entry = f"{summary['timestamp']}: Quality={summary['avg_quality_score']:.1f}, Time={summary['avg_processing_time']:.1f}s, Success={summary['success_rate']*100:.1f}%\n"
        
        with open(self.quality_log, "a") as f:
            f.write(log_entry)
    
    def get_improvement_suggestions(self, summary: Dict) -> List[str]:
        """Generate improvement suggestions based on results"""
        suggestions = []
        
        if summary["avg_quality_score"] < 80:
            suggestions.append("🎯 Focus on analysis depth - ensure 80+ character responses")
        
        if summary["avg_processing_time"] > 12:
            suggestions.append("⚡ Optimize response time - target <12 seconds")
        
        if summary["success_rate"] < 0.95:
            suggestions.append("🔧 Investigate API reliability issues")
        
        # Check individual results for patterns
        brief_analyses = sum(1 for r in summary["results"] if r.get("analysis_length", 0) < 80)
        if brief_analyses > 1:
            suggestions.append(f"📝 {brief_analyses} responses had brief analysis - enhance depth")
        
        slow_responses = sum(1 for r in summary["results"] if r.get("processing_time", 0) > 15)
        if slow_responses > 0:
            suggestions.append(f"🐌 {slow_responses} slow responses (>15s) - investigate bottlenecks")
        
        if not suggestions:
            suggestions.append("🎉 Quality looks good! Consider testing edge cases")
        
        return suggestions
    
    def check_system_resources(self) -> Dict:
        """Check basic system resources"""
        try:
            # Check tmux sessions
            tmux_output = subprocess.run(["tmux", "ls"], capture_output=True, text=True)
            sessions = tmux_output.stdout.count("aigg") if tmux_output.returncode == 0 else 0
            
            # Check disk space
            disk_output = subprocess.run(["df", "-h", "/"], capture_output=True, text=True)
            disk_usage = "Unknown"
            if disk_output.returncode == 0:
                lines = disk_output.stdout.strip().split('\n')
                if len(lines) > 1:
                    disk_usage = lines[1].split()[4]
            
            return {
                "tmux_sessions": sessions,
                "disk_usage": disk_usage,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e)}
    
    def run_monitoring_cycle(self):
        """Run a complete monitoring cycle"""
        print("🚀 AIGG Continuous Improvement Monitor")
        print("=" * 50)
        
        # System check
        resources = self.check_system_resources()
        print(f"💻 System: {resources.get('tmux_sessions', 0)} AIGG sessions, {resources.get('disk_usage', 'N/A')} disk used")
        
        # Quality check
        summary = self.quick_quality_check()
        
        # Log metrics
        self.log_quality_metrics(summary)
        
        # Generate suggestions
        suggestions = self.get_improvement_suggestions(summary)
        
        print(f"\n💡 Improvement Suggestions:")
        for suggestion in suggestions:
            print(f"   {suggestion}")
        
        # Overall assessment
        if summary["avg_quality_score"] >= 85:
            print(f"\n🎉 EXCELLENT: System performing very well!")
        elif summary["avg_quality_score"] >= 75:
            print(f"\n✅ GOOD: System performing well with minor improvements needed")
        elif summary["avg_quality_score"] >= 60:
            print(f"\n⚠️  NEEDS WORK: System needs attention")
        else:
            print(f"\n❌ CRITICAL: System requires immediate fixes")
        
        print("=" * 50)
        
        return summary

def main():
    """Main function for command line usage"""
    monitor = AIGGContinuousMonitor()
    
    try:
        summary = monitor.run_monitoring_cycle()
        return 0 if summary["success_rate"] > 0.8 else 1
    except KeyboardInterrupt:
        print("\n⚠️  Monitoring interrupted")
        return 1
    except Exception as e:
        print(f"\n❌ Monitoring failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 