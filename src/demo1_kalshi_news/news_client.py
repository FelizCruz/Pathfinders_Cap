"""
Minimal News API client for fetching news articles.
"""
import requests
from typing import Dict, List
from datetime import datetime, timedelta
from .config import NewsConfig


class NewsClient:
    """Client for interacting with News API."""
    
    def __init__(self):
        """Initialize the News API client."""
        self.api_url = NewsConfig.API_URL
        self.api_key = NewsConfig.API_KEY
    
    def search_news(self, query: str, max_articles: int = 5) -> List[Dict]:
        """
        Search for news articles related to a query.
        
        Args:
            query: Search query string
            max_articles: Maximum number of articles to return
        
        Returns:
            List of article dictionaries
        """
        try:
            # Get articles from the last 7 days
            from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            
            params = {
                'q': query,
                'apiKey': self.api_key,
                'from': from_date,
                'sortBy': 'relevancy',
                'pageSize': max_articles,
                'language': 'en'
            }
            
            response = requests.get(
                f"{self.api_url}/everything",
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            articles = data.get('articles', [])
            
            print(f"✓ Found {len(articles)} articles for query: '{query}'")
            return articles
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Failed to fetch news for '{query}': {e}")
            return []
    
    def search_multiple_topics(self, topics: List[str], articles_per_topic: int = 3) -> Dict[str, List[Dict]]:
        """
        Search for news articles across multiple topics.
        
        Args:
            topics: List of topic strings to search for
            articles_per_topic: Number of articles to fetch per topic
        
        Returns:
            Dictionary mapping topics to their article lists
        """
        results = {}
        
        for topic in topics:
            articles = self.search_news(topic, max_articles=articles_per_topic)
            if articles:
                results[topic] = articles
        
        total_articles = sum(len(articles) for articles in results.values())
        print(f"✓ Fetched total of {total_articles} articles across {len(results)} topics")
        
        return results
    
    def format_articles_for_analysis(self, articles_by_topic: Dict[str, List[Dict]]) -> str:
        """
        Format news articles into a text summary for AI analysis.
        
        Args:
            articles_by_topic: Dictionary mapping topics to article lists
        
        Returns:
            Formatted text string
        """
        formatted_text = "NEWS ARTICLES SUMMARY:\n\n"
        
        for topic, articles in articles_by_topic.items():
            formatted_text += f"Topic: {topic}\n"
            formatted_text += "=" * 50 + "\n\n"
            
            for idx, article in enumerate(articles, 1):
                title = article.get('title', 'No title')
                description = article.get('description', 'No description')
                source = article.get('source', {}).get('name', 'Unknown source')
                published_at = article.get('publishedAt', 'Unknown date')
                
                formatted_text += f"{idx}. {title}\n"
                formatted_text += f"   Source: {source} | Published: {published_at}\n"
                formatted_text += f"   {description}\n\n"
            
            formatted_text += "\n"
        
        return formatted_text
