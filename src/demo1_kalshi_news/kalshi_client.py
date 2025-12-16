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
        self.email = KalshiConfig.EMAIL
        self.password = KalshiConfig.PASSWORD
        self.token = None
        self.session = requests.Session()
    
    def login(self) -> bool:
        """
        Authenticate with Kalshi API.
        
        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            response = self.session.post(
                f"{self.api_url}/login",
                json={"email": self.email, "password": self.password}
            )
            response.raise_for_status()
            
            data = response.json()
            self.token = data.get('token')
            
            # Set authorization header for future requests
            self.session.headers.update({
                'Authorization': f'Bearer {self.token}'
            })
            
            print("✓ Successfully authenticated with Kalshi API")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Failed to authenticate with Kalshi API: {e}")
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
    
    def get_markets(self, event_ticker: Optional[str] = None, limit: int = 5) -> List[Dict]:
        """
        Fetch prediction markets from Kalshi.
        
        Args:
            event_ticker: Optional event ticker to filter markets
            limit: Maximum number of markets to fetch
        
        Returns:
            List of market dictionaries
        """
        try:
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
            List of topic strings
        """
        topics = []
        
        for event in events:
            # Extract title and category as potential topics
            title = event.get('title', '')
            category = event.get('category', '')
            
            if title:
                topics.append(title)
            if category and category not in topics:
                topics.append(category)
        
        # Clean and limit topics
        topics = [t for t in topics if t][:5]  # Limit to 5 topics
        
        print(f"✓ Extracted {len(topics)} topics from events")
        return topics
