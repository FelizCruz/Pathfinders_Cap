"""
Azure AI analyzer for semantic analysis of combined Kalshi and News data.
"""
from openai import AzureOpenAI
from typing import Dict, List
from .config import AzureConfig


class AzureAnalyzer:
    """Client for Azure OpenAI semantic analysis."""
    
    def __init__(self):
        """Initialize the Azure OpenAI client."""
        self.client = AzureOpenAI(
            azure_endpoint=AzureConfig.ENDPOINT,
            api_key=AzureConfig.API_KEY,
            api_version=AzureConfig.API_VERSION
        )
        self.deployment_name = AzureConfig.DEPLOYMENT_NAME
    
    def analyze_market_news_correlation(
        self, 
        kalshi_data: List[Dict], 
        news_summary: str
    ) -> str:
        """
        Analyze the correlation between Kalshi prediction markets and news sentiment.
        
        Args:
            kalshi_data: List of Kalshi events/markets
            news_summary: Formatted news articles summary
        
        Returns:
            Analysis results as a string
        """
        try:
            # Format Kalshi data for analysis
            kalshi_summary = self._format_kalshi_data(kalshi_data)
            
            # Create the analysis prompt
            prompt = self._create_analysis_prompt(kalshi_summary, news_summary)
            
            print("✓ Sending data to Azure OpenAI for analysis...")
            
            # Call Azure OpenAI
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert analyst specializing in prediction markets and news sentiment analysis. Your task is to analyze how news sentiment correlates with prediction market data and provide insights."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            analysis = response.choices[0].message.content
            
            print("✓ Successfully received analysis from Azure OpenAI")
            return analysis
            
        except Exception as e:
            print(f"✗ Failed to analyze data with Azure OpenAI: {e}")
            return f"Error during analysis: {str(e)}"
    
    def _format_kalshi_data(self, kalshi_data: List[Dict]) -> str:
        """
        Format Kalshi market data for analysis.
        
        Args:
            kalshi_data: List of Kalshi events/markets
        
        Returns:
            Formatted text string
        """
        formatted = "KALSHI PREDICTION MARKET DATA:\n\n"
        
        for idx, item in enumerate(kalshi_data, 1):
            title = item.get('title', 'Unknown event')
            category = item.get('category', 'Unknown category')
            ticker = item.get('ticker', 'N/A')
            
            formatted += f"{idx}. {title}\n"
            formatted += f"   Category: {category}\n"
            formatted += f"   Ticker: {ticker}\n"
            
            # Add market-specific data if available
            if 'yes_bid' in item:
                formatted += f"   Yes Bid: {item.get('yes_bid', 'N/A')}\n"
            if 'no_bid' in item:
                formatted += f"   No Bid: {item.get('no_bid', 'N/A')}\n"
            if 'volume' in item:
                formatted += f"   Volume: {item.get('volume', 'N/A')}\n"
            
            formatted += "\n"
        
        return formatted
    
    def _create_analysis_prompt(self, kalshi_summary: str, news_summary: str) -> str:
        """
        Create the prompt for Azure OpenAI analysis.
        
        Args:
            kalshi_summary: Formatted Kalshi data
            news_summary: Formatted news data
        
        Returns:
            Complete prompt string
        """
        prompt = f"""Analyze the relationship between the following prediction market data and news articles.

{kalshi_summary}

{news_summary}

Please provide:
1. Key themes and correlations between the prediction markets and news sentiment
2. How news sentiment might influence or reflect the prediction market trends
3. Notable insights or patterns you observe
4. Potential implications for future predictions

Provide a clear, structured analysis that synthesizes both data sources."""
        
        return prompt
    
    def extract_key_phrases(self, text: str) -> List[str]:
        """
        Extract key phrases from text using Azure OpenAI.
        
        Args:
            text: Text to analyze
        
        Returns:
            List of key phrases
        """
        try:
            prompt = f"""Extract the top 10 most important key phrases from the following text. Return only the phrases as a comma-separated list.

Text:
{text[:3000]}  # Limit text length
"""
            
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that extracts key phrases from text."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            phrases_text = response.choices[0].message.content
            phrases = [p.strip() for p in phrases_text.split(',')]
            
            print(f"✓ Extracted {len(phrases)} key phrases")
            return phrases
            
        except Exception as e:
            print(f"✗ Failed to extract key phrases: {e}")
            return []
