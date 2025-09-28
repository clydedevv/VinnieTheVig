#!/usr/bin/env python3
"""
AIGG Twitter Bot Whitelist Management Script
Convenient interface for managing bot access
"""

import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.twitter.whitelist_manager import WhitelistManager, AccessLevel

def main():
    """Main whitelist management interface"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="AIGG Bot Whitelist Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add yourself as admin
  python scripts/manage_whitelist.py add 1234567890 your_username --level admin
  
  # Add a beta tester
  python scripts/manage_whitelist.py add 9876543210 beta_user --level whitelist --notes "Beta tester"
  
  # List all users
  python scripts/manage_whitelist.py list
  
  # Show statistics
  python scripts/manage_whitelist.py stats
  
  # Block a user
  python scripts/manage_whitelist.py add 1111111111 spammer --level blocked --notes "Spam account"
  
  # Remove a user
  python scripts/manage_whitelist.py remove 1234567890

Access Levels:
  - admin: Full access, no rate limits, can manage bot
  - vip: Full access, no rate limits  
  - whitelist: Normal access with daily rate limits
  - blocked: No access
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add user command
    add_parser = subparsers.add_parser('add', help='Add user to whitelist')
    add_parser.add_argument('user_id', help='Twitter user ID (numeric)')
    add_parser.add_argument('username', help='Twitter username (without @)')
    add_parser.add_argument('--level', default='whitelist', 
                           choices=['whitelist', 'vip', 'admin', 'blocked'],
                           help='Access level (default: whitelist)')
    add_parser.add_argument('--notes', help='Optional notes about the user')
    
    # List users command
    list_parser = subparsers.add_parser('list', help='List whitelist users')
    list_parser.add_argument('--level', choices=['whitelist', 'vip', 'admin', 'blocked'],
                            help='Filter by access level')
    list_parser.add_argument('--detailed', action='store_true', 
                            help='Show detailed information')
    
    # Stats command
    subparsers.add_parser('stats', help='Show whitelist statistics')
    
    # Remove user command
    remove_parser = subparsers.add_parser('remove', help='Remove user from whitelist')
    remove_parser.add_argument('user_id', help='Twitter user ID to remove')
    
    # Update user command
    update_parser = subparsers.add_parser('update', help='Update user access level')
    update_parser.add_argument('user_id', help='Twitter user ID')
    update_parser.add_argument('level', choices=['whitelist', 'vip', 'admin', 'blocked'],
                              help='New access level')
    
    # Enable/disable whitelist
    toggle_parser = subparsers.add_parser('toggle', help='Enable/disable whitelist')
    toggle_parser.add_argument('state', choices=['on', 'off'], 
                              help='Turn whitelist on or off')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize whitelist manager
    try:
        manager = WhitelistManager()
        print(f"📋 AIGG Bot Whitelist Manager")
        print(f"   Whitelist file: {manager.whitelist_file}")
        print(f"   Whitelist enabled: {manager.whitelist_enabled}")
        print()
    except Exception as e:
        print(f"❌ Error initializing whitelist manager: {e}")
        return
    
    # Execute commands
    if args.command == 'add':
        try:
            access_level = AccessLevel(args.level.lower())
            success = manager.add_user(
                user_id=args.user_id,
                username=args.username,
                access_level=access_level,
                added_by="admin",
                notes=args.notes
            )
            
            if success:
                print(f"✅ Added @{args.username} ({args.user_id}) as {args.level}")
                if args.notes:
                    print(f"   Notes: {args.notes}")
            else:
                print(f"❌ Failed to add @{args.username}")
                
        except ValueError:
            print(f"❌ Invalid access level: {args.level}")
    
    elif args.command == 'list':
        level_filter = AccessLevel(args.level) if args.level else None
        users = manager.list_users(level_filter)
        
        if not users:
            print("📭 No users found")
            return
        
        print(f"📋 Whitelist Users ({len(users)} total)")
        print("=" * 80)
        
        if args.detailed:
            for user in users:
                print(f"@{user.username}")
                print(f"   User ID: {user.user_id}")
                print(f"   Level: {user.access_level.value}")
                print(f"   Added: {user.added_date[:10]} by {user.added_by}")
                print(f"   Requests: {user.request_count}")
                if user.notes:
                    print(f"   Notes: {user.notes}")
                print()
        else:
            # Compact view
            print(f"{'Username':<20} {'Level':<10} {'Requests':<8} {'Added':<12}")
            print("-" * 80)
            for user in users:
                added_date = user.added_date[:10] if user.added_date else "Unknown"
                print(f"@{user.username:<19} {user.access_level.value:<10} {user.request_count:<8} {added_date}")
    
    elif args.command == 'stats':
        stats = manager.get_whitelist_stats()
        
        print(f"📊 Whitelist Statistics")
        print("=" * 30)
        print(f"Total users: {stats['total_users']}")
        print(f"Whitelist enabled: {stats['whitelist_enabled']}")
        print(f"Requests today: {stats['total_requests_today']}")
        print(f"Max requests per day: {manager.max_requests_per_day}")
        
        if stats['by_access_level']:
            print("\nBy access level:")
            for level, count in stats['by_access_level'].items():
                print(f"  {level}: {count} users")
        
        # Show recent activity
        users = manager.list_users()
        active_today = [u for u in users if u.last_request and 
                       u.last_request.startswith(str(datetime.now().date()))]
        
        if active_today:
            print(f"\nActive today: {len(active_today)} users")
            for user in sorted(active_today, key=lambda x: x.request_count, reverse=True)[:5]:
                print(f"  @{user.username}: {user.request_count} requests")
    
    elif args.command == 'remove':
        success = manager.remove_user(args.user_id)
        if success:
            print(f"✅ Removed user {args.user_id} from whitelist")
        else:
            print(f"❌ User {args.user_id} not found in whitelist")
    
    elif args.command == 'update':
        try:
            new_level = AccessLevel(args.level.lower())
            success = manager.update_access_level(args.user_id, new_level)
            
            if success:
                user = manager.whitelist.get(args.user_id)
                username = user.username if user else args.user_id
                print(f"✅ Updated @{username} to {args.level}")
            else:
                print(f"❌ User {args.user_id} not found in whitelist")
                
        except ValueError:
            print(f"❌ Invalid access level: {args.level}")
    
    elif args.command == 'toggle':
        # This would require modifying environment variables or config
        print(f"⚠️  Whitelist toggle not implemented yet")
        print(f"    Current state: {'ON' if manager.whitelist_enabled else 'OFF'}")
        print(f"    To change: Set WHITELIST_ENABLED=true/false in .env file")

def get_user_id_from_username(username: str) -> str:
    """Helper to get user ID from username (would need Twitter API)"""
    print(f"💡 To get user ID for @{username}:")
    print(f"   1. Go to https://tweeterid.com/")
    print(f"   2. Enter: {username}")
    print(f"   3. Copy the numeric ID")
    return ""

if __name__ == "__main__":
    from datetime import datetime
    main() 