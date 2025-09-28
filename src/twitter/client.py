#!/usr/bin/env python3
"""
Twitter Client for AIGG Insights
Handles mentions, extracts prediction market queries, and posts AI analysis
"""

import tweepy
import os
import re
import time
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from dotenv import load_dotenv

# Add whitelist import
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from src.twitter.whitelist_manager import WhitelistManager

load_dotenv()

@dataclass
class TweetQuery:
    """Extracted prediction market query from a tweet"""
    tweet_id: str
    user_handle: str
    user_id: str
    original_text: str
    extracted_query: str
    confidence: float  # How confident we are this is a prediction market query

@dataclass
class AIGGResponse:
    """Response to send back to Twitter"""
    market_title: str
    analysis: str
    recommendation: str
    confidence: float
    polymarket_url: str
    tweet_text: str  # Formatted for Twitter

class TwitterClient:
    """Twitter client for AIGG prediction market analysis"""
    
    def __init__(self):
        """Initialize Twitter client with API credentials"""
        self.setup_logging()
        self.setup_twitter_api()
        self.bot_handle = "@vigvinnie"  # Actual bot username
        
        # Initialize whitelist manager
        self.whitelist_manager = WhitelistManager()
        
        # Rate limiting
        self.last_response_time = {}  # user_id -> timestamp
        self.min_response_interval = 300  # 5 minutes between responses per user
        
    def setup_logging(self):
        """Setup logging for Twitter operations"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/twitter_bot.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_twitter_api(self):
        """Setup Twitter API v2 client"""
        try:
            # Twitter API v2 credentials
            self.client = tweepy.Client(
                bearer_token=os.getenv('TWITTER_BEARER_TOKEN'),
                consumer_key=os.getenv('TWITTER_API_KEY'),
                consumer_secret=os.getenv('TWITTER_API_SECRET'),
                access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
                access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET'),
                wait_on_rate_limit=True
            )
            
            # Hard-code bot info to avoid API calls during initialization
            # These values are known and won't change
            self.bot_user_id = "1929305566611947520"  # @vigvinnie user ID  
            self.bot_username = "vigvinnie"  # Bot username without @
            
            self.logger.info(f"Twitter API client initialized for @{self.bot_username}")
                
        except Exception as e:
            self.logger.error(f"Twitter API setup failed: {e}")
            raise
    
    def extract_prediction_query(self, tweet_text: str) -> Optional[TweetQuery]:
        """Extract prediction market query from tweet text"""
        # Remove mentions and URLs
        clean_text = re.sub(r'@\w+', '', tweet_text)
        clean_text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', clean_text)
        clean_text = clean_text.strip()
        
        # Prediction market keywords/patterns
        prediction_patterns = [
            r'will\s+.*\?',
            r'who\s+will\s+.*\?',
            r'who\s+.*\s+(gonna|going to)\s+.*',  # "who is gonna have"
            r'when\s+will\s+.*\?',
            r'what\s+will\s+.*\?',
            r'.*\s+price\s+.*\?',
            r'.*\s+reach\s+.*\?',
            r'.*\s+hit\s+.*\?',
            r'.*\s+election.*',  # Removed \? requirement
            r'.*\s+winner\s+.*\?',
            r'.*\s+odds\s+.*',
            r'should\s+i\s+.*bet\s+.*',  # More flexible
            r'who\s+should\s+i\s+.*bet\s+.*',  # Added for your case
            r'what\s+should\s+i\s+bet\s+.*',
            r'.*\s+happening\s+.*\?',
            r'.*\s+best\s+.*',  # "best model", "best ai", etc.
            r'prediction\s+.*',
            r'forecast\s+.*',
            r'.*pick.*bet.*',  # Added for "pick to bet"
            r'.*mayoral.*election.*',  # Specific for mayoral elections
            r'what.*move.*',  # "what's the move"
            r'.*guilty.*',  # guilty/conviction questions
            r'.*found.*guilty.*',  # specific guilty patterns
            r'.*convicted.*',  # conviction patterns
            r'do\s+you\s+think.*',  # "do you think perplexity will..."
            r'.*\s+will\s+.*manage\s+to.*',  # "will manage to acquire"
            r'.*\s+acquire.*',  # acquisition questions
            r'.*\s+merger.*',  # merger questions
            r'.*likely.*to.*',  # "likely to happen"
            r'chances.*of.*',  # "chances of X happening"
        ]
        
        confidence = 0.0
        
        # Check for prediction patterns
        for pattern in prediction_patterns:
            if re.search(pattern, clean_text, re.IGNORECASE):
                confidence += 0.3
        
        # Market-specific keywords (expanded for conversational responses)
        market_keywords = [
            'bitcoin', 'btc', 'crypto', 'ethereum', 'election', 'president', 
            'trump', 'biden', 'nba', 'finals', 'championship', 'stock', 
            'tesla', 'apple', 'google', 'ai', 'nuclear', 'war', 'peace',
            'federal reserve', 'fed', 'interest rate', 'inflation',
            'mayor', 'mayoral', 'nyc', 'new york', 'bet',  # Added betting/political keywords
            'diddy', 'p diddy', 'guilty', 'conviction', 'trafficking', 'trial',  # Legal/celebrity keywords
            'court', 'verdict', 'sentence', 'charges',  # More legal keywords
            'khamenei', 'supreme leader', 'iran', 'ceasefire', 'israel', 'hamas',  # Geopolitical keywords
            'ukraine', 'russia', 'wimbledon', 'tesla', 'robotaxi',  # Sports/tech keywords
            'perplexity', 'chrome', 'microsoft', 'openai', 'acquisition', 'merger', 'acquire',  # Tech/business keywords
            'model', 'best model', 'ai model', 'llm', 'gpt', 'claude', 'odds',  # AI model keywords + odds
            # Light conversational triggers (smaller boost)
            'prediction', 'forecast', 'market', 'price', 'value', 'worth', 'cost', 
            'buy', 'sell', 'invest', 'money', 'happening', 'news', 'update', 'latest'
        ]
        
        for keyword in market_keywords:
            if keyword.lower() in clean_text.lower():
                confidence += 0.1  # Reduced from 0.2 to be less aggressive
        
        # Question marks increase confidence
        if '?' in clean_text:
            confidence += 0.3
        
        # Betting-related queries get bonus confidence
        if any(word in clean_text.lower() for word in ['bet', 'betting', 'should i', 'pick']):
            confidence += 0.3
        
        # If this is a mention of the bot, always respond (even with 0 confidence)
        if '@vigvinnie' in tweet_text.lower() or '@VigVinnie' in tweet_text:
            # Give minimum confidence to any direct mention
            confidence = max(confidence, 0.1)
        
        # Very low confidence threshold - respond to almost everything
        if confidence < 0.1:
            return None
            
        return TweetQuery(
            tweet_id="",  # Will be filled by caller
            user_handle="",  # Will be filled by caller
            user_id="",  # Will be filled by caller
            original_text=tweet_text,
            extracted_query=clean_text,
            confidence=min(confidence, 1.0)
        )
    
    def format_response_for_twitter(self, analysis_result, original_query: str) -> str:
        """Format AIGG analysis result for Twitter constraints"""
        # Twitter character limit is 280
        base_template = "🔍 {query}\n📊 {analysis}\n📈 {recommendation}\n🔗 {url}"
        
        # Truncate analysis if too long
        max_analysis_length = 120
        analysis = analysis_result.analysis
        if len(analysis) > max_analysis_length:
            analysis = analysis[:max_analysis_length-3] + "..."
        
        # Format recommendation with confidence
        rec_text = f"{analysis_result.recommendation} ({analysis_result.confidence:.0%} confidence)"
        
        # Build tweet
        formatted_tweet = base_template.format(
            query=original_query[:60] + "..." if len(original_query) > 60 else original_query,
            analysis=analysis,
            recommendation=rec_text,
            url=analysis_result.polymarket_url
        )
        
        # If still too long, truncate analysis more aggressively
        if len(formatted_tweet) > 280:
            max_analysis = 280 - len(formatted_tweet) + len(analysis) - 10
            analysis = analysis[:max_analysis] + "..."
            formatted_tweet = base_template.format(
                query=original_query[:60] + "..." if len(original_query) > 60 else original_query,
                analysis=analysis,
                recommendation=rec_text,
                url=analysis_result.polymarket_url
            )
        
        return formatted_tweet
    
    def can_respond_to_user(self, user_id: str) -> bool:
        """Check if we can respond to user (rate limiting)"""
        # Allow admin users to bypass rate limiting for testing
        if str(user_id) == "195487174":  # clydedevv admin user ID
            self.logger.debug(f"Admin user {user_id} bypassing rate limit")
            return True
            
        now = time.time()
        last_response = self.last_response_time.get(user_id, 0)
        time_since = now - last_response
        self.logger.debug(f"Rate limit check for {user_id}: {time_since:.1f}s since last (need {self.min_response_interval}s)")
        return time_since >= self.min_response_interval
    
    def record_response_to_user(self, user_id: str):
        """Record that we responded to a user"""
        self.last_response_time[user_id] = time.time()
    
    def get_mentions(self, since_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get recent mentions of the bot"""
        try:
            # Use cached username instead of calling get_me() every time
            query = f"@{self.bot_username}"
            
            # Search for recent tweets mentioning the bot
            tweets = self.client.search_recent_tweets(
                query=query,
                since_id=since_id,
                max_results=10,
                tweet_fields=['id', 'text', 'created_at', 'author_id', 'public_metrics', 'conversation_id'],
                user_fields=['username'],
                # Include referenced tweets so we can inspect parent when this is a reply
                expansions=['author_id', 'referenced_tweets.id', 'attachments.media_keys'],
                media_fields=['media_key', 'type', 'url', 'preview_image_url', 'alt_text']
            )
            
            if not tweets.data:
                return []
            
            # Process tweets with user and media info
            users = {}
            if tweets.includes and 'users' in tweets.includes:
                users = {user.id: user for user in tweets.includes['users']}
            media_map = {}
            if tweets.includes and 'media' in tweets.includes:
                # Map media_key -> media object
                media_map = {m.media_key: m for m in tweets.includes['media']}
            # Map of referenced tweets (e.g., parent tweets for replies)
            referenced = {}
            if tweets.includes and 'tweets' in tweets.includes:
                referenced = {t.id: t for t in tweets.includes['tweets']}
            
            processed_tweets = []
            for tweet in tweets.data:
                # Skip our own tweets
                if tweet.author_id == self.bot_user_id:
                    continue
                    
                author = users.get(tweet.author_id)
                # Attempt to extract parent (replied_to) tweet info
                parent_id = None
                parent_text = None
                try:
                    if getattr(tweet, 'referenced_tweets', None):
                        for ref in tweet.referenced_tweets:
                            if getattr(ref, 'type', None) == 'replied_to':
                                parent_id = ref.id
                                # If expanded tweet is available, grab its text
                                if parent_id in referenced:
                                    parent_text = referenced[parent_id].text
                                break
                except Exception:
                    parent_id = None
                    parent_text = None
                # Collect image URLs if present
                media_urls = []
                try:
                    attachments = getattr(tweet, 'attachments', None)
                    if attachments and isinstance(attachments, dict) and 'media_keys' in attachments:
                        for mkey in attachments['media_keys']:
                            mobj = media_map.get(mkey)
                            if not mobj:
                                continue
                            mtype = getattr(mobj, 'type', None)
                            if mtype == 'photo':
                                url = getattr(mobj, 'url', None) or getattr(mobj, 'preview_image_url', None)
                                if url:
                                    media_urls.append(url)
                except Exception:
                    media_urls = []
                processed_tweets.append({
                    'id': tweet.id,
                    'text': tweet.text,
                    'author_id': tweet.author_id,
                    'author_username': author.username if author else 'unknown',
                    'created_at': tweet.created_at,
                    # New fields to enable reading parent tweet when this is a reply
                    'parent_id': parent_id,
                    'parent_text': parent_text,
                    # Image URLs attached to this tweet (photos only)
                    'media_urls': media_urls
                })
            
            return processed_tweets
            
        except Exception as e:
            self.logger.error(f"Error getting mentions: {e}")
            return []

    def fetch_tweet_text(self, tweet_id: str) -> Optional[str]:
        """Fetch a tweet's text by ID as a lightweight fallback.

        Used when a mention is a reply but the parent tweet's text wasn't
        included in the expansions. This avoids extra calls unless needed.
        """
        try:
            resp = self.client.get_tweet(
                id=tweet_id,
                tweet_fields=['id', 'text', 'created_at']
            )
            if resp and getattr(resp, 'data', None):
                return getattr(resp.data, 'text', None)
            return None
        except Exception as e:
            self.logger.error(f"Error fetching tweet {tweet_id}: {e}")
            return None

    def fetch_tweet_media_urls(self, tweet_id: str) -> List[str]:
        """Fetch photo media URLs for a tweet by ID.

        Returns a list of direct image URLs (photos only). Empty list if none.
        """
        try:
            resp = self.client.get_tweet(
                id=tweet_id,
                expansions=['attachments.media_keys'],
                media_fields=['media_key', 'type', 'url', 'preview_image_url']
            )
            urls: List[str] = []
            if not resp or not getattr(resp, 'includes', None):
                return urls
            media_list = resp.includes.get('media', [])
            for m in media_list:
                mtype = getattr(m, 'type', None)
                if mtype == 'photo':
                    url = getattr(m, 'url', None) or getattr(m, 'preview_image_url', None)
                    if url:
                        urls.append(url)
            return urls
        except Exception as e:
            self.logger.error(f"Error fetching media for tweet {tweet_id}: {e}")
            return []
    
    def reply_to_tweet(self, tweet_id: str, response_text: str) -> bool:
        """Reply to a specific tweet"""
        try:
            response = self.client.create_tweet(
                text=response_text,
                in_reply_to_tweet_id=tweet_id
            )
            
            if response.data:
                self.logger.info(f"Successfully replied to tweet {tweet_id}")
                return True
            else:
                self.logger.error(f"Failed to reply to tweet {tweet_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error replying to tweet {tweet_id}: {e}")
            return False
    
    def process_mention(self, tweet: Dict[str, Any]) -> bool:
        """Process a single mention and respond if appropriate"""
        try:
            # Check whitelist access first
            user_id = tweet['author_id']
            username = tweet['author_username']
            
            access_allowed, reason = self.whitelist_manager.is_access_allowed(user_id, username)
            if not access_allowed:
                self.logger.info(f"Access denied for @{username}: {reason}")
                
                # Optionally send a polite denial message (only for whitelist, not blocked users)
                if "not in whitelist" in reason:
                    denial_message = "🤖 Thanks for your interest! This bot is currently in beta testing with limited access. Follow us for updates on public availability!"
                    self.reply_to_tweet(tweet['id'], denial_message)
                
                return False
            
            # Record the request for rate limiting
            self.whitelist_manager.record_request(user_id)
            
            # Extract query
            query = self.extract_prediction_query(tweet['text'])
            if not query:
                self.logger.info(f"No prediction query found in tweet {tweet['id']}")
                return False
            
            # Fill in tweet details
            query.tweet_id = tweet['id']
            query.user_handle = tweet['author_username']
            query.user_id = tweet['author_id']
            
            # Check rate limiting (Twitter client level)
            if not self.can_respond_to_user(query.user_id):
                self.logger.info(f"Rate limited for user {query.user_handle}")
                return False
            
            self.logger.info(f"Processing query from @{query.user_handle}: {query.extracted_query}")
            
            # Here we'll integrate with our AIGG flow
            # For now, return a placeholder response
            response_text = f"🤖 Analyzing your prediction market query...\n📊 Query: {query.extracted_query[:100]}\n🔄 This is a test response!"
            
            # Reply to tweet
            success = self.reply_to_tweet(tweet['id'], response_text)
            if success:
                self.record_response_to_user(query.user_id)
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error processing mention {tweet['id']}: {e}")
            return False

# Test function
def test_twitter_client():
    """Test the Twitter client functionality"""
    client = TwitterClient()
    
    # Test query extraction
    test_tweets = [
        "Will Bitcoin reach $150k this year?",
        "@aigg_bot what are the odds of Trump winning the election?",
        "Should I bet on the Lakers to win the NBA championship?",
        "Just had lunch",  # Should not be detected
        "When will the Fed raise interest rates next?",
    ]
    
    print("Testing query extraction:")
    for tweet in test_tweets:
        query = client.extract_prediction_query(tweet)
        if query:
            print(f"✅ '{tweet}' -> '{query.extracted_query}' (confidence: {query.confidence:.2f})")
        else:
            print(f"❌ '{tweet}' -> No query detected")

if __name__ == "__main__":
    test_twitter_client() 