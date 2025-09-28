#!/usr/bin/env python3
"""
AIGG Twitter Bot - Main Bot Implementation
Integrates Twitter client with AIGG analysis wrapper API
"""

import sys
import os
import time
import requests
import json
import asyncio
import logging
from typing import Optional, Set, List, Dict, Any

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.twitter.client import TwitterClient
from src.twitter.whitelist_manager import WhitelistManager

class AIGGTwitterBot:
    """Main AIGG Twitter Bot that monitors mentions and responds with AI analysis"""
    
    def __init__(self, wrapper_api_url: str = "http://localhost:8003"):
        """Initialize the Twitter bot"""
        self.wrapper_api_url = wrapper_api_url
        self.setup_logging()
        
        # Persistent state (deduplication and resume)
        self.state_file = os.path.join("data", "twitter_bot_state.json")
        self._replied_capacity = 2000  # keep last N replied tweet IDs
        self.replied_tweet_ids: Set[str] = set()
        self.replied_tweet_ids_order: List[str] = []
        
        # Initialize whitelist manager
        self.whitelist_manager = WhitelistManager()
        
        # Initialize Twitter client (will fail gracefully if no credentials)
        try:
            self.twitter_client = TwitterClient()
            self.authenticated = True
            self.logger.info("Twitter client initialized successfully")
        except Exception as e:
            self.logger.warning(f"Twitter client initialization failed: {e}")
            self.authenticated = False
        
        # Bot state
        self.last_mention_id = None
        self._load_state()
        self.running = False
        
    def setup_logging(self):
        """Setup logging configuration"""
        os.makedirs("logs", exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)  # Changed to DEBUG level
        
        # File handler
        file_handler = logging.FileHandler('logs/aigg_twitter_bot.log')
        file_handler.setLevel(logging.DEBUG)  # Changed to DEBUG level
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def test_wrapper_api(self) -> bool:
        """Test if wrapper API is available"""
        try:
            response = requests.get(f"{self.wrapper_api_url}/health", timeout=5)
            if response.status_code == 200:
                self.logger.info("Wrapper API is healthy")
                return True
            else:
                self.logger.error(f"Wrapper API health check failed: {response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"Cannot connect to wrapper API: {e}")
            return False
    
    def _load_state(self) -> None:
        """Load persisted state: last mention ID and replied tweet IDs."""
        try:
            os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
            if not os.path.exists(self.state_file):
                return
            with open(self.state_file, 'r') as f:
                data = json.load(f)
            # last_mention_id may be str or int, keep as str for API usage
            if data.get('last_mention_id'):
                self.last_mention_id = str(data['last_mention_id'])
            # replied IDs list
            replied_list = data.get('replied_tweet_ids', [])
            if isinstance(replied_list, list):
                # normalize to strings
                self.replied_tweet_ids_order = [str(x) for x in replied_list][-self._replied_capacity:]
                self.replied_tweet_ids = set(self.replied_tweet_ids_order)
            self.logger.info(
                f"Loaded state: last_mention_id={self.last_mention_id}, replied_ids={len(self.replied_tweet_ids)}"
            )
        except Exception as e:
            self.logger.warning(f"Failed to load state file: {e}")
    
    def _save_state(self) -> None:
        """Persist last mention ID and replied tweet IDs to disk."""
        try:
            os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
            state = {
                'last_mention_id': self.last_mention_id,
                'replied_tweet_ids': self.replied_tweet_ids_order[-self._replied_capacity:],
            }
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Failed to save state file: {e}")
    
    def get_ai_analysis(self, query: str, user_id: str, user_handle: str, tweet_id: str, media_urls: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """Get AI analysis from wrapper API
        
        Returns:
            Dict with 'tweet_text' and optionally 'follow_up_tweet' if available,
            or None on error
        """
        try:
            payload = {
                "query": query,
                "user_id": user_id,
                "user_handle": user_handle,
                "tweet_id": tweet_id
            }
            if media_urls:
                payload["media_urls"] = media_urls
            
            response = requests.post(
                f"{self.wrapper_api_url}/analyze",
                json=payload,
                timeout=90  # AI analysis can take time, especially with LLM optimization
            )
            
            if response.status_code == 200:
                data = response.json()
                if data["success"]:
                    self.logger.info(f"AI analysis successful for @{user_handle} in {data['processing_time']:.2f}s")
                    # Return full data including follow_up_tweet if present
                    result = {"tweet_text": data["tweet_text"]}
                    if data.get("has_follow_up") and data.get("follow_up_tweet"):
                        result["follow_up_tweet"] = data["follow_up_tweet"]
                        self.logger.info(f"Follow-up tweet available for @{user_handle}")
                    return result
                else:
                    self.logger.warning(f"AI analysis failed for @{user_handle}: {data.get('error_message', 'Unknown error')}")
                    return {"tweet_text": data["tweet_text"]}  # Return error message
            elif response.status_code == 429:
                self.logger.info(f"Rate limited for user @{user_handle}")
                return {"tweet_text": "⏱️ You're asking me too frequently! Please wait a few minutes before your next question."}
            else:
                self.logger.error(f"Wrapper API error {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error calling wrapper API: {e}")
            return None
    
    def process_mentions(self):
        """Process new mentions and respond appropriately"""
        if not self.authenticated:
            self.logger.warning("Not authenticated with Twitter API")
            return
        
        try:
            # Get new mentions
            mentions = self.twitter_client.get_mentions(since_id=self.last_mention_id)
            
            if not mentions:
                return
            
            self.logger.info(f"Processing {len(mentions)} new mentions")
            # Track max ID seen in this batch to advance the cursor once per batch
            try:
                batch_max_id = max(int(str(m['id'])) for m in mentions)
            except Exception:
                batch_max_id = None
            
            for mention in mentions:
                self.logger.info(f"Processing mention from @{mention['author_username']}: {mention['text'][:100]}")
                # Skip if we already replied to this mention (dedup across restarts)
                mention_id_str = str(mention['id'])
                if mention_id_str in self.replied_tweet_ids:
                    self.logger.info(f"Skipping already-handled mention {mention_id_str}")
                    continue
                
                # Additional check: see if we've already replied to this tweet via API
                # This catches cases where state file was lost or corrupted
                try:
                    # Check if bot has already replied to this specific tweet
                    search_query = f"from:{self.twitter_client.bot_username} to:{mention['author_username']}"
                    recent_replies = self.twitter_client.client.search_recent_tweets(
                        query=search_query,
                        max_results=10
                    )
                    if recent_replies and recent_replies.data:
                        for reply in recent_replies.data:
                            # Check if this is a reply to the current mention
                            if hasattr(reply, 'referenced_tweets'):
                                for ref in reply.referenced_tweets:
                                    if ref.type == 'replied_to' and str(ref.id) == mention_id_str:
                                        self.logger.info(f"Already replied to mention {mention_id_str} (found via API)")
                                        # Add to our tracking to avoid checking again
                                        self.replied_tweet_ids.add(mention_id_str)
                                        self.replied_tweet_ids_order.append(mention_id_str)
                                        continue
                except Exception as e:
                    self.logger.debug(f"Could not check for existing replies: {e}")
                
                # Check whitelist access (already done in client, but double-check here)
                access_allowed, reason = self.whitelist_manager.is_access_allowed(
                    mention['author_id'], mention['author_username']
                )
                
                # Debug logging to identify the whitelist issue
                self.logger.debug(f"Whitelist check for user_id='{mention['author_id']}' username='{mention['author_username']}': allowed={access_allowed}, reason={reason}")
                
                if not access_allowed:
                    self.logger.info(f"Skipping @{mention['author_username']}: {reason}")
                    continue
                
                # Extract prediction query - handle simple replies like "odds?" that need parent context
                mention_text = mention['text']
                query = self.twitter_client.extract_prediction_query(mention_text)
                
                # Check if this is a simple query like "odds?" that needs parent context
                simple_queries = ['odds?', 'odds', 'what are the odds?', 'chances?', 'probability?']
                is_simple_query = any(simple in mention_text.lower().strip().replace('@vigvinnie', '').strip() 
                                     for simple in simple_queries)
                
                # If it's a simple query OR no query found, try to use parent tweet for context
                if is_simple_query or not query:
                    parent_text = mention.get('parent_text')
                    parent_id = mention.get('parent_id')
                    
                    # Fetch parent text if not already available
                    if not parent_text and parent_id:
                        parent_text = self.twitter_client.fetch_tweet_text(str(parent_id))
                    
                    if parent_text:
                        if is_simple_query:
                            # Combine the simple query with parent context
                            self.logger.info(f"Combining simple query '{mention_text}' with parent tweet context")
                            combined_text = f"{parent_text} {mention_text}"
                            query = self.twitter_client.extract_prediction_query(combined_text)
                            if query:
                                # Update the extracted query to be more specific
                                query.extracted_query = f"{query.extracted_query} (from parent: {parent_text[:100]}...)"
                        else:
                            # Just try parent alone as fallback
                            self.logger.info(f"No query in reply {mention['id']}; attempting parent tweet {parent_id}")
                            query = self.twitter_client.extract_prediction_query(parent_text)
                
                if not query:
                    self.logger.info(f"No prediction query detected in mention {mention['id']} (and no usable parent)")
                    continue
                
                # Check rate limiting
                if not self.twitter_client.can_respond_to_user(mention['author_id']):
                    self.logger.info(f"Rate limited for user @{mention['author_username']}")
                    continue
                
                # Get AI analysis
                # Include image URLs when available (from the mention; fallback to parent if none)
                media_urls = mention.get('media_urls') or []
                if not media_urls and mention.get('parent_id'):
                    try:
                        media_urls = self.twitter_client.fetch_tweet_media_urls(str(mention['parent_id']))
                    except Exception:
                        media_urls = []
                response_data = self.get_ai_analysis(
                    query.extracted_query,
                    str(mention['author_id']),
                    mention['author_username'],
                    str(mention['id']),
                    media_urls
                )
                
                if response_data:
                    # Reply to tweet with main response
                    main_tweet_text = response_data.get("tweet_text")
                    main_reply_response = self.twitter_client.client.create_tweet(
                        text=main_tweet_text,
                        in_reply_to_tweet_id=mention['id']
                    )
                    
                    if main_reply_response.data:
                        main_tweet_id = main_reply_response.data['id']
                        self.twitter_client.record_response_to_user(mention['author_id'])
                        self.whitelist_manager.record_request(mention['author_id'])
                        self.logger.info(f"Successfully replied to @{mention['author_username']} with tweet {main_tweet_id}")
                        
                        # Post follow-up tweet as reply to main tweet (creates proper thread)
                        if response_data.get("follow_up_tweet"):
                            time.sleep(1)  # Small delay before follow-up
                            follow_up_success = self.twitter_client.reply_to_tweet(
                                main_tweet_id,  # Reply to our main tweet, not the original mention
                                response_data["follow_up_tweet"]
                            )
                            if follow_up_success:
                                self.logger.info(f"Posted follow-up tweet in thread for @{mention['author_username']}")
                            else:
                                self.logger.error(f"Failed to post follow-up tweet for @{mention['author_username']}")
                        
                        # Record dedup info
                        if mention_id_str not in self.replied_tweet_ids:
                            self.replied_tweet_ids.add(mention_id_str)
                            self.replied_tweet_ids_order.append(mention_id_str)
                            # Bound memory
                            if len(self.replied_tweet_ids_order) > self._replied_capacity:
                                drop = self.replied_tweet_ids_order[:-self._replied_capacity]
                                self.replied_tweet_ids_order = self.replied_tweet_ids_order[-self._replied_capacity:]
                                for old_id in drop:
                                    self.replied_tweet_ids.discard(old_id)
                            # Save promptly to avoid duplicates after crash
                            self._save_state()
                    else:
                        self.logger.error(f"Failed to reply to @{mention['author_username']}")
                else:
                    self.logger.error(f"No response generated for @{mention['author_username']}")
                
                # Small delay between responses
                time.sleep(2)
                
        except Exception as e:
            self.logger.error(f"Error processing mentions: {e}")
        finally:
            # Advance cursor once per batch (prevents reprocessing and duplication)
            if 'batch_max_id' in locals() and batch_max_id is not None:
                self.last_mention_id = str(batch_max_id)
                self._save_state()
    
    def run_monitoring_loop(self, check_interval: int = 30):  # X Premium: 30 seconds
        """Run the main monitoring loop"""
        self.logger.info(f"Starting AIGG Twitter Bot monitoring (check interval: {check_interval}s)")
        
        # Check prerequisites
        if not self.test_wrapper_api():
            self.logger.error("Wrapper API not available. Exiting.")
            return
        
        if not self.authenticated:
            self.logger.error("Twitter API not authenticated. Exiting.")
            return
        
        self.running = True
        
        try:
            while self.running:
                self.logger.debug("Checking for new mentions...")
                self.process_mentions()
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            self.logger.info("Bot stopped by user")
        except Exception as e:
            self.logger.error(f"Bot error: {e}")
        finally:
            self.running = False
            self.logger.info("AIGG Twitter Bot stopped")
    
    def stop(self):
        """Stop the bot"""
        self.running = False

def main():
    """Main function to run the bot"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AIGG Twitter Bot")
    parser.add_argument("--api-url", default="http://localhost:8003", help="Wrapper API URL")
    parser.add_argument("--check-interval", type=int, default=30, help="Check interval in seconds (X Premium: 30s)")
    parser.add_argument("--test-only", action="store_true", help="Test setup and exit")
    parser.add_argument("--whitelist-stats", action="store_true", help="Show whitelist stats and exit")
    
    args = parser.parse_args()
    
    # Initialize bot
    bot = AIGGTwitterBot(wrapper_api_url=args.api_url)
    
    if args.whitelist_stats:
        stats = bot.whitelist_manager.get_whitelist_stats()
        print("\n📊 AIGG Bot Whitelist Statistics")
        print("=" * 40)
        print(f"Total users: {stats['total_users']}")
        print(f"Whitelist enabled: {stats['whitelist_enabled']}")
        print(f"Requests today: {stats['total_requests_today']}")
        print("\nBy access level:")
        for level, count in stats['by_access_level'].items():
            print(f"  {level}: {count}")
        return
    
    if args.test_only:
        print("🤖 Testing AIGG Twitter Bot Setup...")
        
        # Test wrapper API
        api_ok = bot.test_wrapper_api()
        print(f"✅ Wrapper API: {'OK' if api_ok else '❌ FAILED'}")
        
        # Test Twitter authentication
        print(f"✅ Twitter Auth: {'OK' if bot.authenticated else '❌ FAILED'}")
        
        # Test whitelist
        stats = bot.whitelist_manager.get_whitelist_stats()
        print(f"✅ Whitelist: {stats['total_users']} users, enabled: {stats['whitelist_enabled']}")
        
        if bot.authenticated:
            # Test query extraction
            test_tweets = [
                "Will Bitcoin reach $150k this year?",
                "@aigg_bot what are the odds of Trump winning?",
                "Should I bet on the Lakers?",
            ]
            
            print("\n🔍 Testing query extraction:")
            for tweet in test_tweets:
                query = bot.twitter_client.extract_prediction_query(tweet)
                if query:
                    print(f"✅ '{tweet}' -> '{query.extracted_query}' (confidence: {query.confidence:.2f})")
                else:
                    print(f"❌ '{tweet}' -> No query detected")
        
        print(f"\n{'🚀 Ready to run!' if (api_ok and bot.authenticated) else '❌ Setup incomplete'}")
        return
    
    # Run the bot
    bot.run_monitoring_loop(check_interval=args.check_interval)

if __name__ == "__main__":
    main() 