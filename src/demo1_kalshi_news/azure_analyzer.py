"""
AI analyzer for semantic analysis of combined Kalshi and News data.
Supports GitHub Models, Azure OpenAI, and OpenAI endpoints.
"""
from openai import OpenAI
from typing import Dict, List
from datetime import datetime
from .config import AzureConfig


class AzureAnalyzer:
    """Client for OpenAI/GitHub Models semantic analysis."""
    
    def __init__(self):
        """Initialize the OpenAI client (GitHub Models compatible)."""
        self.client = OpenAI(
            base_url=AzureConfig.ENDPOINT,
            api_key=AzureConfig.API_KEY
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
    
    def analyze_with_relevance_filter(
        self,
        user_query: str,
        kalshi_data: List[Dict],
        news_summary: str
    ) -> str:
        """
        Analyze data with explicit instruction to filter out irrelevant content.
        
        Args:
            user_query: The user's original search query
            kalshi_data: List of Kalshi events/markets
            news_summary: Formatted news articles summary
        
        Returns:
            Analysis results as a string
        """
        try:
            kalshi_summary = self._format_kalshi_data(kalshi_data)
            
            prompt = f"""USER QUERY: "{user_query}"

{kalshi_summary}

{news_summary}

ANALYSIS INSTRUCTIONS:
1. FIRST, identify which news articles and prediction markets are DIRECTLY relevant to the user's query "{user_query}".
2. EXCLUDE any articles or markets that are not directly related to the query topic.
3. For RELEVANT prediction markets, explain what the Yes/No percentages indicate about market sentiment.
4. Analyze the sentiment of RELEVANT news articles (positive, negative, neutral).
5. Identify correlations between news sentiment and market predictions.
6. Provide a clear summary of what the data suggests about "{user_query}".

FORMAT YOUR RESPONSE AS:
**Relevant Data Summary:**
- List only the relevant markets and articles you're analyzing

**Market Sentiment:**
- What do the prediction market probabilities suggest?

**News Sentiment:**
- What is the overall tone of relevant news coverage?

**Key Insights:**
- How do news and market data correlate?
- What does this suggest about the topic?

**Conclusion:**
- Brief, actionable takeaway for the user
"""

            print("✓ Sending data for relevance-filtered analysis...")
            
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert analyst specializing in prediction markets and news sentiment analysis. 
                        
CRITICAL: You must ONLY analyze data that is DIRECTLY relevant to the user's query. 
- If a news article or market is not clearly related to the query topic, EXCLUDE it from your analysis.
- Be explicit about what you're including and excluding.
- Focus on providing actionable insights based on relevant data only."""
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
            print("✓ Successfully received filtered analysis")
            return analysis
            
        except Exception as e:
            print(f"✗ Failed to analyze: {e}")
            return f"Error during analysis: {str(e)}"
    
    def analyze_event_with_news(
        self,
        event_title: str,
        yes_pct: float,
        no_pct: float,
        news_summary: str,
        market_summary: str = None
    ) -> str:
        """
        Analyze a specific prediction market event with related news.
        
        Args:
            event_title: Title of the Kalshi event
            yes_pct: Yes probability percentage (top outcome for multi-outcome)
            no_pct: No probability percentage
            news_summary: Formatted news articles summary
            market_summary: Full market context including all outcomes (optional)
        
        Returns:
            AI analysis of market + news correlation
        """
        try:
            current_date = datetime.now().strftime("%B %d, %Y")
            
            # Use full market summary if provided, otherwise build basic one
            if market_summary:
                market_context = market_summary
            else:
                market_context = f"""PREDICTION MARKET EVENT: "{event_title}"

CURRENT MARKET DATA:
- YES Probability: {yes_pct:.1f}%
- NO Probability: {no_pct:.1f}%
- Market Sentiment: {"Bullish (Yes favored)" if yes_pct > 55 else "Bearish (No favored)" if no_pct > 55 else "Uncertain/Split"}"""

            prompt = f"""TODAY'S DATE: {current_date}

{market_context}

{news_summary}

ANALYSIS TASK:
1. Analyze what the market probability ({yes_pct:.1f}% YES) suggests about expected outcomes.
2. Examine the news articles for information that might explain the current market pricing.
3. Identify any news events that could be driving market sentiment up or down.
4. Look for potential disconnects between news sentiment and market pricing.
5. Provide insights on what could cause the market to move.

FORMAT YOUR RESPONSE AS:

**Market Interpretation:**
Brief explanation of what the {yes_pct:.1f}% YES probability means in plain terms.

**News Impact Analysis:**
Which news stories are most relevant? How do they relate to market pricing?

**Sentiment Alignment:**
Does the news sentiment match the market sentiment? Any disconnects?

**Price Movement Factors:**
What news developments could push the probability higher or lower?

**Key Takeaway:**
One-paragraph summary for a trader or analyst."""

            print(f"✓ Analyzing event: {event_title[:50]}...")
            
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are an expert prediction market analyst who specializes in correlating news sentiment with market probabilities.

IMPORTANT: Today's date is {current_date}. The 2024 US election is in the PAST. Any references to future elections mean 2028 or later.

Your analysis should be:
- Data-driven: Reference specific probabilities and news details
- Actionable: Provide insights a trader could use
- Balanced: Consider both bull and bear cases
- Clear: Use plain language, avoid jargon
- Time-aware: Consider what events are past vs future"""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1200
            )
            
            analysis = response.choices[0].message.content
            print("✓ Event analysis complete")
            return analysis
            
        except Exception as e:
            print(f"✗ Failed to analyze event: {e}")
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
{text[:3000]}"""
            
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
