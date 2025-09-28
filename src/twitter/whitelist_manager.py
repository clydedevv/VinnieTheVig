#!/usr/bin/env python3
"""
Whitelist Manager for AIGG Twitter Bot
Controls who can interact with the bot
"""

import json
import os
import logging
from typing import Set, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

class AccessLevel(Enum):
    """Access levels for users"""
    BLOCKED = "blocked"
    WHITELIST = "whitelist"
    VIP = "vip"
    ADMIN = "admin"

@dataclass
class WhitelistEntry:
    """Entry in the whitelist"""
    user_id: str
    username: str
    access_level: AccessLevel
    added_date: str
    added_by: str
    notes: Optional[str] = None
    request_count: int = 0
    last_request: Optional[str] = None

class WhitelistManager:
    """Manages bot access control via whitelist"""
    
    def __init__(self, whitelist_file: str = "config/whitelist.json"):
        """Initialize whitelist manager"""
        self.whitelist_file = whitelist_file
        self.setup_logging()
        self.whitelist: dict[str, WhitelistEntry] = {}
        self.load_whitelist()
        
        # Configuration
        self.whitelist_enabled = os.getenv('WHITELIST_ENABLED', 'true').lower() == 'true'
        self.max_requests_per_day = int(os.getenv('MAX_REQUESTS_PER_DAY', '10'))
        
    def setup_logging(self):
        """Setup logging"""
        self.logger = logging.getLogger(__name__)
    
    def load_whitelist(self):
        """Load whitelist from file"""
        try:
            if os.path.exists(self.whitelist_file):
                with open(self.whitelist_file, 'r') as f:
                    data = json.load(f)
                    
                for user_id, entry_data in data.items():
                    # Convert string back to enum
                    entry_data['access_level'] = AccessLevel(entry_data['access_level'])
                    self.whitelist[user_id] = WhitelistEntry(**entry_data)
                    
                self.logger.info(f"Loaded {len(self.whitelist)} entries from whitelist")
            else:
                self.logger.info("No whitelist file found, starting with empty whitelist")
                # Create default entries
                self._create_default_whitelist()
                
        except Exception as e:
            self.logger.error(f"Error loading whitelist: {e}")
            self._create_default_whitelist()
    
    def save_whitelist(self):
        """Save whitelist to file"""
        try:
            os.makedirs(os.path.dirname(self.whitelist_file), exist_ok=True)
            
            # Convert to serializable format
            data = {}
            for user_id, entry in self.whitelist.items():
                entry_dict = asdict(entry)
                entry_dict['access_level'] = entry.access_level.value
                data[user_id] = entry_dict
            
            with open(self.whitelist_file, 'w') as f:
                json.dump(data, f, indent=2)
                
            self.logger.info(f"Saved whitelist with {len(self.whitelist)} entries")
            
        except Exception as e:
            self.logger.error(f"Error saving whitelist: {e}")
    
    def _create_default_whitelist(self):
        """Create default whitelist with admin user"""
        # Add your Twitter user ID here as admin
        admin_user_id = os.getenv('ADMIN_USER_ID', 'your_user_id_here')
        admin_username = os.getenv('ADMIN_USERNAME', 'your_username')
        
        if admin_user_id != 'your_user_id_here':
            self.add_user(
                user_id=admin_user_id,
                username=admin_username,
                access_level=AccessLevel.ADMIN,
                added_by="system",
                notes="Default admin user"
            )
    
    def is_access_allowed(self, user_id: str, username: str) -> tuple[bool, str]:
        """
        Check if user has access to the bot
        Returns (allowed, reason)
        """
        # If whitelist is disabled, allow everyone (for public launch)
        if not self.whitelist_enabled:
            return True, "Public access enabled"
        
        # Check if user is in whitelist
        if user_id not in self.whitelist:
            return False, "User not in whitelist"
        
        entry = self.whitelist[user_id]
        
        # Check access level
        if entry.access_level == AccessLevel.BLOCKED:
            return False, "User is blocked"
        
        # Check daily request limit (except for VIP and admin)
        if entry.access_level not in [AccessLevel.VIP, AccessLevel.ADMIN]:
            if self._check_daily_limit(entry):
                return False, f"Daily limit exceeded ({self.max_requests_per_day} requests)"
        
        return True, f"Access granted ({entry.access_level.value})"
    
    def _check_daily_limit(self, entry: WhitelistEntry) -> bool:
        """Check if user has exceeded daily request limit"""
        if not entry.last_request:
            return False
        
        try:
            last_request = datetime.fromisoformat(entry.last_request.replace('Z', '+00:00'))
            today = datetime.now().date()
            
            # If last request was today, check count
            if last_request.date() == today:
                return entry.request_count >= self.max_requests_per_day
            
            # Reset daily count if it's a new day
            return False
            
        except Exception:
            return False
    
    def record_request(self, user_id: str):
        """Record a request from a user"""
        if user_id in self.whitelist:
            entry = self.whitelist[user_id]
            now = datetime.now()
            
            # Reset count if it's a new day
            if entry.last_request:
                try:
                    last_request = datetime.fromisoformat(entry.last_request.replace('Z', '+00:00'))
                    if last_request.date() != now.date():
                        entry.request_count = 0
                except Exception:
                    entry.request_count = 0
            
            entry.request_count += 1
            entry.last_request = now.isoformat()
            
            # Save periodically (every 10 requests)
            if entry.request_count % 10 == 0:
                self.save_whitelist()
    
    def add_user(self, user_id: str, username: str, access_level: AccessLevel, 
                 added_by: str, notes: Optional[str] = None) -> bool:
        """Add user to whitelist"""
        try:
            entry = WhitelistEntry(
                user_id=user_id,
                username=username,
                access_level=access_level,
                added_date=datetime.now().isoformat(),
                added_by=added_by,
                notes=notes
            )
            
            self.whitelist[user_id] = entry
            self.save_whitelist()
            
            self.logger.info(f"Added @{username} ({user_id}) to whitelist as {access_level.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding user to whitelist: {e}")
            return False
    
    def remove_user(self, user_id: str) -> bool:
        """Remove user from whitelist"""
        try:
            if user_id in self.whitelist:
                username = self.whitelist[user_id].username
                del self.whitelist[user_id]
                self.save_whitelist()
                
                self.logger.info(f"Removed @{username} ({user_id}) from whitelist")
                return True
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"Error removing user from whitelist: {e}")
            return False
    
    def update_access_level(self, user_id: str, new_level: AccessLevel) -> bool:
        """Update user's access level"""
        try:
            if user_id in self.whitelist:
                old_level = self.whitelist[user_id].access_level
                self.whitelist[user_id].access_level = new_level
                self.save_whitelist()
                
                username = self.whitelist[user_id].username
                self.logger.info(f"Updated @{username} access: {old_level.value} → {new_level.value}")
                return True
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"Error updating access level: {e}")
            return False
    
    def get_whitelist_stats(self) -> dict:
        """Get whitelist statistics"""
        stats = {
            'total_users': len(self.whitelist),
            'by_access_level': {},
            'total_requests_today': 0,
            'whitelist_enabled': self.whitelist_enabled
        }
        
        today = datetime.now().date()
        
        for entry in self.whitelist.values():
            level = entry.access_level.value
            stats['by_access_level'][level] = stats['by_access_level'].get(level, 0) + 1
            
            # Count today's requests
            if entry.last_request:
                try:
                    last_request = datetime.fromisoformat(entry.last_request.replace('Z', '+00:00'))
                    if last_request.date() == today:
                        stats['total_requests_today'] += entry.request_count
                except Exception:
                    pass
        
        return stats
    
    def list_users(self, access_level: Optional[AccessLevel] = None) -> List[WhitelistEntry]:
        """List users, optionally filtered by access level"""
        users = list(self.whitelist.values())
        
        if access_level:
            users = [u for u in users if u.access_level == access_level]
        
        # Sort by username
        users.sort(key=lambda x: x.username.lower())
        return users

# Admin command functions
def add_user_command(manager: WhitelistManager, user_id: str, username: str, 
                    level: str = "whitelist", notes: str = None):
    """Command line function to add user"""
    try:
        access_level = AccessLevel(level.lower())
        success = manager.add_user(user_id, username, access_level, "admin", notes)
        if success:
            print(f"✅ Added @{username} as {level}")
        else:
            print(f"❌ Failed to add @{username}")
    except ValueError:
        print(f"❌ Invalid access level: {level}")
        print("Valid levels: whitelist, vip, admin, blocked")

def main():
    """CLI for whitelist management"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AIGG Bot Whitelist Manager")
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Add user
    add_parser = subparsers.add_parser('add', help='Add user to whitelist')
    add_parser.add_argument('user_id', help='Twitter user ID')
    add_parser.add_argument('username', help='Twitter username (without @)')
    add_parser.add_argument('--level', default='whitelist', 
                           choices=['whitelist', 'vip', 'admin', 'blocked'],
                           help='Access level')
    add_parser.add_argument('--notes', help='Optional notes')
    
    # List users
    list_parser = subparsers.add_parser('list', help='List whitelist users')
    list_parser.add_argument('--level', choices=['whitelist', 'vip', 'admin', 'blocked'],
                            help='Filter by access level')
    
    # Stats
    subparsers.add_parser('stats', help='Show whitelist statistics')
    
    # Remove user
    remove_parser = subparsers.add_parser('remove', help='Remove user from whitelist')
    remove_parser.add_argument('user_id', help='Twitter user ID')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = WhitelistManager()
    
    if args.command == 'add':
        add_user_command(manager, args.user_id, args.username, args.level, args.notes)
    
    elif args.command == 'list':
        level = AccessLevel(args.level) if args.level else None
        users = manager.list_users(level)
        
        print(f"\n📋 Whitelist Users ({len(users)} total)")
        print("-" * 60)
        for user in users:
            print(f"@{user.username:20} {user.access_level.value:10} {user.request_count:3} reqs")
    
    elif args.command == 'stats':
        stats = manager.get_whitelist_stats()
        print(f"\n📊 Whitelist Statistics")
        print("-" * 30)
        print(f"Total users: {stats['total_users']}")
        print(f"Whitelist enabled: {stats['whitelist_enabled']}")
        print(f"Requests today: {stats['total_requests_today']}")
        print("\nBy access level:")
        for level, count in stats['by_access_level'].items():
            print(f"  {level}: {count}")
    
    elif args.command == 'remove':
        success = manager.remove_user(args.user_id)
        if success:
            print(f"✅ Removed user {args.user_id}")
        else:
            print(f"❌ User {args.user_id} not found")

if __name__ == "__main__":
    main() 