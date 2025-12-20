"""
Minimal Kalshi API client for fetching prediction market data.
"""
import requests
from typing import Dict, List, Optional
from .config import KalshiConfig


class KalshiClient:
    """Client for interacting with Kalshi prediction market API."""
    
    def __init__(self):
        """Initialize the Kalshi client."""
        self.api_url = KalshiConfig.API_URL
        self.api_key = KalshiConfig.API_KEY
        self.session = requests.Session()
        # Set API key header only if provided (for authenticated access)
        if self.api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {self.api_key}'
            })
    
    def login(self) -> bool:
        """
        Verify connection to Kalshi API (works with or without API key).
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Test connection by fetching events
            response = self.session.get(f"{self.api_url}/events", params={'limit': 1})
            response.raise_for_status()
            
            if self.api_key:
                print("✓ Successfully connected to Kalshi API (authenticated)")
            else:
                print("✓ Successfully connected to Kalshi API (public)")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Failed to connect to Kalshi API: {e}")
            return False
    
    def get_events(self, limit: int = 5, status: str = 'open') -> List[Dict]:
        """
        Fetch prediction market events from Kalshi.
        
        Args:
            limit: Maximum number of events to fetch
            status: Event status filter (e.g., 'open', 'closed')
        
        Returns:
            List of event dictionaries
        """
        try:
            params = {
                'limit': limit,
                'status': status
            }
            
            response = self.session.get(
                f"{self.api_url}/events",
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            events = data.get('events', [])
            
            print(f"✓ Fetched {len(events)} events from Kalshi")
            return events
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Failed to fetch events from Kalshi: {e}")
            return []
    
    def get_markets(self, event_ticker: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """
        Fetch prediction markets from Kalshi with price data.
        
        Args:
            event_ticker: Optional event ticker to filter markets
            limit: Maximum number of markets to fetch
        
        Returns:
            List of market dictionaries with price data
        """
        try:
            # Try to get markets for this specific event
            if event_ticker:
                # Try the event-specific endpoint first
                response = self.session.get(
                    f"{self.api_url}/events/{event_ticker}"
                )
                if response.status_code == 200:
                    data = response.json()
                    event_data = data.get('event', data)
                    markets = event_data.get('markets', [])
                    if markets:
                        print(f"✓ Fetched {len(markets)} markets for event {event_ticker}")
                        return markets
            
            # Fallback to general markets endpoint
            params = {
                'limit': limit,
                'status': 'open'
            }
            
            if event_ticker:
                params['event_ticker'] = event_ticker
            
            response = self.session.get(
                f"{self.api_url}/markets",
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            markets = data.get('markets', [])
            
            print(f"✓ Fetched {len(markets)} markets from Kalshi")
            return markets
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Failed to fetch markets from Kalshi: {e}")
            return []
    
    def extract_topics(self, events: List[Dict]) -> List[str]:
        """
        Extract relevant topics/keywords from Kalshi events for news search.
        
        Args:
            events: List of event dictionaries from Kalshi
        
        Returns:
            List of topic strings (specific keywords, not broad categories)
        """
        topics = []
        
        # Common words to filter out (too broad or not useful for search)
        stop_words = {
            'will', 'the', 'be', 'in', 'on', 'at', 'to', 'a', 'an', 'of', 'for',
            'before', 'after', 'by', 'his', 'her', 'their', 'this', 'that',
            'world', 'politics', 'economics', 'other', 'general', 'yes', 'no',
            'happen', 'occur', 'during', 'between', 'within', 'lifetime',
            'who', 'what', 'when', 'where', 'why', 'how', 'which', 'next'
        }
        
        for event in events:
            title = event.get('title', '')
            
            if title:
                # Extract key phrases from title
                # Look for proper nouns, names, specific terms
                words = title.replace('?', '').replace("'s", '').split()
                
                # Find capitalized words (likely proper nouns/names)
                key_terms = []
                i = 0
                while i < len(words):
                    word = words[i]
                    # Check if it's a capitalized word (proper noun)
                    if word[0].isupper() and word.lower() not in stop_words:
                        # Try to capture multi-word names (e.g., "Elon Musk", "Federal Reserve")
                        phrase = [word]
                        j = i + 1
                        while j < len(words) and words[j][0].isupper() and words[j].lower() not in stop_words:
                            phrase.append(words[j])
                            j += 1
                        key_terms.append(' '.join(phrase))
                        i = j
                    else:
                        i += 1
                
                # Add extracted terms
                for term in key_terms:
                    if term and term not in topics and len(term) > 2:
                        topics.append(term)
        
        # If no specific topics found, extract from titles more aggressively
        if not topics:
            for event in events:
                title = event.get('title', '')
                # Use first few meaningful words
                words = [w for w in title.split()[:4] if w.lower() not in stop_words]
                if words:
                    topics.append(' '.join(words))
        
        # Limit to 5 unique topics
        topics = list(dict.fromkeys(topics))[:5]
        
        print(f"✓ Extracted {len(topics)} specific topics: {topics}")
        return topics
