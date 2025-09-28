#!/usr/bin/env python3
"""
AIGG Insights Health Check Script
Monitors all services and provides comprehensive status report
"""

import os
import sys
import json
import time
import requests
import subprocess
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

class HealthChecker:
    """Health check for all AIGG services"""
    
    def __init__(self):
        self.status = {
            "timestamp": datetime.now().isoformat(),
            "services": {},
            "database": {},
            "system": {},
            "alerts": []
        }
    
    def check_market_api(self) -> Dict[str, Any]:
        """Check Market API health"""
        try:
            response = requests.get("http://37.27.54.184:8001/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "healthy",
                    "response_time": response.elapsed.total_seconds(),
                    "market_count": data.get("market_count", 0),
                    "version": data.get("version", "unknown")
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": f"Status code: {response.status_code}"
                }
        except requests.exceptions.ConnectionError:
            return {"status": "offline", "error": "Connection refused"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def check_wrapper_api(self) -> Dict[str, Any]:
        """Check Twitter Wrapper API health"""
        try:
            response = requests.get("http://localhost:8003/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "healthy",
                    "response_time": response.elapsed.total_seconds(),
                    "rate_limit": data.get("rate_limit", {}),
                    "version": data.get("version", "unknown")
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": f"Status code: {response.status_code}"
                }
        except requests.exceptions.ConnectionError:
            return {"status": "offline", "error": "Connection refused"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def check_database(self) -> Dict[str, Any]:
        """Check database via remote API"""
        try:
            # Get database stats from remote API health endpoint
            response = requests.get("http://37.27.54.184:8001/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "healthy",
                    "connection": "remote API",
                    "stats": {
                        "total_markets": data.get("total_markets", 0),
                        "active_markets": data.get("active_markets", 0)
                    },
                    "source": "production server"
                }
            else:
                return {"status": "unhealthy", "error": f"API returned {response.status_code}"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def check_twitter_bot(self) -> Dict[str, Any]:
        """Check Twitter bot status via tmux or process"""
        try:
            # Check tmux session (if tmux is available)
            in_tmux = False
            try:
                result = subprocess.run(
                    ["tmux", "list-sessions"], 
                    capture_output=True, 
                    text=True,
                    check=False
                )
                in_tmux = "aigg-bot" in result.stdout if result.returncode == 0 else False
            except FileNotFoundError:
                # tmux not installed
                pass
            
            # Check for running process
            ps_result = subprocess.run(
                ["ps", "aux"], 
                capture_output=True, 
                text=True,
                check=False
            )
            in_process = "twitter-bot" in ps_result.stdout
            
            # Check bot logs
            log_file = "/tmp/aigg_twitter_bot.log"
            last_activity = None
            if os.path.exists(log_file):
                stat = os.stat(log_file)
                last_activity = datetime.fromtimestamp(stat.st_mtime)
            
            status = "healthy" if (in_tmux or in_process) else "offline"
            
            return {
                "status": status,
                "in_tmux": in_tmux,
                "in_process": in_process,
                "last_activity": last_activity.isoformat() if last_activity else None,
                "stale": (datetime.now() - last_activity > timedelta(minutes=20)) if last_activity else True
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def check_system_resources(self) -> Dict[str, Any]:
        """Check system resources"""
        try:
            # Disk usage
            df_result = subprocess.run(
                ["df", "-h", "/"], 
                capture_output=True, 
                text=True,
                check=True
            )
            disk_lines = df_result.stdout.strip().split('\n')
            if len(disk_lines) > 1:
                disk_parts = disk_lines[1].split()
                disk_usage = disk_parts[4] if len(disk_parts) > 4 else "unknown"
            else:
                disk_usage = "unknown"
            
            # Memory usage
            free_result = subprocess.run(
                ["free", "-m"], 
                capture_output=True, 
                text=True,
                check=False
            )
            
            # Load average
            with open('/proc/loadavg', 'r') as f:
                load_avg = f.read().strip().split()[:3]
            
            return {
                "disk_usage": disk_usage,
                "load_average": load_avg,
                "status": "healthy"
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def generate_alerts(self):
        """Generate alerts based on health check results"""
        # Service alerts
        for service, data in self.status["services"].items():
            if data.get("status") != "healthy":
                self.status["alerts"].append({
                    "level": "critical" if data.get("status") == "offline" else "warning",
                    "service": service,
                    "message": f"{service} is {data.get('status')}: {data.get('error', 'Unknown error')}"
                })
        
        # Database alerts
        if self.status["database"].get("status") != "healthy":
            self.status["alerts"].append({
                "level": "critical",
                "service": "database",
                "message": "Database connection failed"
            })
        
        # Twitter bot staleness
        bot_data = self.status["services"].get("twitter_bot", {})
        if bot_data.get("stale"):
            self.status["alerts"].append({
                "level": "warning",
                "service": "twitter_bot",
                "message": "Twitter bot has not been active for over 20 minutes"
            })
        
        # Disk usage alert
        disk_usage = self.status["system"].get("disk_usage", "0%")
        if disk_usage != "unknown":
            usage_percent = int(disk_usage.rstrip('%'))
            if usage_percent > 90:
                self.status["alerts"].append({
                    "level": "critical",
                    "service": "system",
                    "message": f"Disk usage critical: {disk_usage}"
                })
            elif usage_percent > 80:
                self.status["alerts"].append({
                    "level": "warning",
                    "service": "system",
                    "message": f"Disk usage high: {disk_usage}"
                })
    
    def run_health_check(self, output_format: str = "console") -> Dict[str, Any]:
        """Run complete health check"""
        print("🏥 Running AIGG Insights Health Check...")
        
        # Check all services
        self.status["services"]["market_api"] = self.check_market_api()
        self.status["services"]["wrapper_api"] = self.check_wrapper_api()
        self.status["services"]["twitter_bot"] = self.check_twitter_bot()
        
        # Check database
        self.status["database"] = self.check_database()
        
        # Check system
        self.status["system"] = self.check_system_resources()
        
        # Generate alerts
        self.generate_alerts()
        
        # Output results
        if output_format == "json":
            print(json.dumps(self.status, indent=2))
        else:
            self.print_console_report()
        
        return self.status
    
    def print_console_report(self):
        """Print formatted console report"""
        print("\n" + "=" * 60)
        print("📊 AIGG INSIGHTS HEALTH REPORT")
        print("=" * 60)
        print(f"🕐 Timestamp: {self.status['timestamp']}")
        print("\n📡 SERVICES:")
        print("-" * 40)
        
        # Service status
        for service, data in self.status["services"].items():
            status = data.get("status", "unknown")
            emoji = "✅" if status == "healthy" else "❌" if status == "offline" else "⚠️"
            print(f"{emoji} {service.replace('_', ' ').title()}: {status.upper()}")
            
            if status == "healthy" and "response_time" in data:
                print(f"   └─ Response time: {data['response_time']:.3f}s")
            elif status != "healthy" and "error" in data:
                print(f"   └─ Error: {data['error']}")
        
        # Database status
        print("\n🗄️  DATABASE (Remote):")
        print("-" * 40)
        db = self.status["database"]
        if db.get("status") == "healthy":
            stats = db.get("stats", {})
            print(f"✅ Connection: {db.get('connection', 'Established')}")
            print(f"   ├─ Total markets: {stats.get('total_markets', 0):,}")
            print(f"   ├─ Active markets: {stats.get('active_markets', 0):,}")
            print(f"   └─ Source: {db.get('source', 'unknown')}")
        else:
            print(f"❌ Connection: Failed - {db.get('error', 'Unknown error')}")
        
        # System resources
        print("\n💻 SYSTEM:")
        print("-" * 40)
        sys_info = self.status["system"]
        if sys_info.get("status") == "healthy":
            print(f"📊 Disk usage: {sys_info.get('disk_usage', 'unknown')}")
            print(f"📈 Load average: {', '.join(sys_info.get('load_average', ['unknown']))}")
        
        # Alerts
        if self.status["alerts"]:
            print("\n⚠️  ALERTS:")
            print("-" * 40)
            for alert in self.status["alerts"]:
                level_emoji = "🔴" if alert["level"] == "critical" else "🟡"
                print(f"{level_emoji} [{alert['level'].upper()}] {alert['service']}: {alert['message']}")
        else:
            print("\n✅ No alerts - All systems operational")
        
        print("\n" + "=" * 60)

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AIGG Insights Health Check")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--watch", action="store_true", help="Run continuously")
    parser.add_argument("--interval", type=int, default=60, help="Check interval in seconds (for watch mode)")
    
    args = parser.parse_args()
    
    checker = HealthChecker()
    
    if args.watch:
        print(f"🔄 Running health check every {args.interval} seconds...")
        print("Press Ctrl+C to stop")
        try:
            while True:
                os.system('clear' if os.name == 'posix' else 'cls')
                checker.run_health_check("json" if args.json else "console")
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\n👋 Health check stopped")
    else:
        checker.run_health_check("json" if args.json else "console")
        
        # Exit with error code if critical alerts
        critical_alerts = [a for a in checker.status["alerts"] if a["level"] == "critical"]
        if critical_alerts:
            sys.exit(1)

if __name__ == "__main__":
    main()