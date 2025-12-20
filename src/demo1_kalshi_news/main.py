"""
Demo 1: Kalshi API + News API Integration
Main orchestration script that combines prediction market data with news data
and uses Azure AI for semantic analysis.
"""
import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

from demo1_kalshi_news.config import validate_all_configs
from demo1_kalshi_news.kalshi_client import KalshiClient
from demo1_kalshi_news.news_client import NewsClient
from demo1_kalshi_news.azure_analyzer import AzureAnalyzer
from demo1_kalshi_news.text_analytics_client import TextAnalyticsClient
from demo1_kalshi_news.powerbi_export import PowerBIExporter


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def main():
    """Main demo pipeline."""
    print_section("DEMO 1: Kalshi + News API + Azure AI Integration")
    
    # Step 0: Validate configuration
    print_section("Step 0: Validating Configuration")
    try:
        validate_all_configs()
    except ValueError as e:
        print(f"\n✗ Configuration Error: {e}")
        print("\nPlease create a .env file based on .env.example and fill in your credentials.")
        return 1
    
    # Step 1: Initialize clients
    print_section("Step 1: Initializing API Clients")
    kalshi_client = KalshiClient()
    news_client = NewsClient()
    azure_analyzer = AzureAnalyzer()
    text_analytics = TextAnalyticsClient()
    print("✓ All clients initialized (including Text Analytics)")
    
    # Step 2: Authenticate and fetch Kalshi data
    print_section("Step 2: Fetching Kalshi Prediction Market Data")
    
    if not kalshi_client.login():
        print("\n⚠ Failed to authenticate with Kalshi. Continuing with sample data.")
        print("Note: If you don't have Kalshi credentials, this is expected.")
        print("The demo will use sample topics to demonstrate the pipeline.")
        # For demo purposes, create mock data
        kalshi_events = []
    else:
        kalshi_events = kalshi_client.get_events(limit=5)
    
    # If no events, use sample topics for demonstration
    if not kalshi_events:
        print("\n⚠ No Kalshi events fetched. Using sample topics for demonstration.")
        sample_topics = ["2024 Presidential Election", "Federal Reserve Interest Rates", "Climate Policy"]
        kalshi_events = [
            {"title": topic, "category": "Politics/Economics", "ticker": f"DEMO-{i}"}
            for i, topic in enumerate(sample_topics, 1)
        ]
    
    print(f"\nKalshi Events Summary:")
    for event in kalshi_events:
        print(f"  - {event.get('title', 'Unknown')}")
    
    # Step 3: Extract topics and fetch related news
    print_section("Step 3: Fetching Related News Articles")
    
    topics = kalshi_client.extract_topics(kalshi_events)
    if not topics:
        topics = ["politics", "economy"]  # Fallback topics
        print("⚠ Using fallback topics: politics, economy")
    
    news_by_topic = news_client.search_multiple_topics(topics, articles_per_topic=3)
    
    if not news_by_topic:
        print("\n✗ No news articles fetched. Please check your NEWS_API_KEY.")
        print("The demo would normally fetch news articles related to Kalshi events here.")
        return 1
    
    # Step 4: Format data for analysis
    print_section("Step 4: Preparing Data for Azure AI Analysis")
    news_summary = news_client.format_articles_for_analysis(news_by_topic)
    print(f"✓ Formatted {len(news_by_topic)} topics worth of news data")
    
    # Step 5: Perform Azure AI analysis
    print_section("Step 5: Analyzing with Azure OpenAI")
    analysis = azure_analyzer.analyze_market_news_correlation(
        kalshi_data=kalshi_events,
        news_summary=news_summary
    )
    
    # Step 6: Display results
    print_section("Step 6: Analysis Results")
    print(analysis)
    
    # Step 7: Azure Text Analytics - Sentiment & Key Phrases
    print_section("Step 7: Azure Text Analytics (Language Service)")
    
    # Extract article texts for analysis
    article_texts = []
    for topic, articles in news_by_topic.items():
        for article in articles:
            title = article.get('title', '')
            description = article.get('description', '')
            if title or description:
                article_texts.append(f"{title}. {description}")
    
    if article_texts:
        # Run text analytics
        ta_results = text_analytics.analyze_all(article_texts[:10])  # Limit to 10 for demo
        
        # Display formatted results
        print(text_analytics.format_results_summary(ta_results))
    else:
        print("⚠ No article texts available for Text Analytics")
    
    # Optional: Extract key phrases using Azure OpenAI
    print_section("Bonus: Key Phrase Extraction (Azure OpenAI)")
    combined_text = news_summary + "\n" + str(kalshi_events)
    key_phrases = azure_analyzer.extract_key_phrases(combined_text)
    
    if key_phrases:
        print("Top Key Phrases:")
        for idx, phrase in enumerate(key_phrases[:10], 1):
            print(f"  {idx}. {phrase}")
    
    # Step 8: Export data for Power BI
    print_section("Step 8: Exporting Data for Power BI Dashboard")
    powerbi_exporter = PowerBIExporter()
    
    # Get sentiment results if available
    sentiment_results = ta_results.get('sentiment', []) if 'ta_results' in dir() else []
    
    export_paths = powerbi_exporter.export_all(
        kalshi_events=kalshi_events,
        news_data=news_by_topic,
        analysis=analysis,
        sentiment_results=sentiment_results
    )
    
    print("\n📊 Power BI Data Files:")
    for export_type, path in export_paths.items():
        print(f"  • {export_type}: {path}")
    
    print("\n💡 To use in Power BI:")
    print("  1. Open Power BI Desktop")
    print("  2. Get Data → Text/CSV or JSON")
    print("  3. Navigate to the 'output/powerbi' folder")
    print("  4. Import the CSV/JSON files")
    print("  5. Create visualizations from the imported data")
    
    print_section("Demo Complete!")
    print("✓ Successfully demonstrated Kalshi + News API + Azure AI integration")
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n✗ Demo interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
