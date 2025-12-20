# Demo 1: Kalshi API + News API + Azure AI Integration


This demo provides a Streamlit dashboard that integrates Kalshi prediction market data with news from News API, and uses Azure OpenAI (or GitHub Models) for semantic analysis to understand correlations between market predictions and news sentiment.

**Power BI integration is deprecated. All results are now visualized in the Streamlit dashboard.**

## Overview


## Dashboard Logic

1. **Category Selection**: User selects a prediction market category (e.g. Politics, Economy)
2. **Event Selection**: User chooses a market event (e.g. "Next US Presidential Election Winner?")
3. **Market Visualization**: Dashboard displays a pie chart of all mutually exclusive outcomes (e.g. candidate probabilities)
4. **News Fetching**: Related news articles are fetched using a smart query (top candidate + context)
5. **AI Analysis**: GPT-5 (via Azure OpenAI or GitHub Models) analyzes how news sentiment relates to market probabilities

## Prerequisites

- Python 3.8 or higher
- Azure OpenAI account with a deployed model
- Kalshi API account (optional - demo works with sample data)
- News API key (get free key at [https://newsapi.org/](https://newsapi.org/))

## Setup

### 1. Install Dependencies

From the repository root:

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
# Azure OpenAI Configuration (Required)
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_KEY=your-azure-openai-api-key
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Kalshi API Configuration (Optional - demo uses sample data if not provided)
KALSHI_API_URL=https://api.elections.kalshi.com/trade-api/v2
KALSHI_EMAIL=your-kalshi-email@example.com
KALSHI_PASSWORD=your-kalshi-password

# News API Configuration (Required)
NEWS_API_KEY=your-news-api-key
NEWS_API_URL=https://newsapi.org/v2
```

**Note:**
- Azure OpenAI and News API credentials are required for the demo to run
- Kalshi credentials are optional - the demo will use sample topics if not provided


## Running the Dashboard

From the repository root:

```bash
streamlit run src/demo1_kalshi_news/dashboard.py
```


## Expected Output

The dashboard will:

1. Validate all API credentials
2. Connect to Kalshi API and fetch prediction market events
3. Display categories and events for user selection
4. Show pie chart of market probabilities (all outcomes)
5. Fetch and display relevant news articles
6. Send combined data to Azure OpenAI for analysis
7. Display:
   - Market probabilities (pie chart)
   - Related news articles
   - AI-generated analysis of correlations


## File Structure

```
src/demo1_kalshi_news/
├── config.py           # Environment configuration and validation
├── kalshi_client.py    # Kalshi API client
├── news_client.py      # News API client
├── azure_analyzer.py   # Azure OpenAI integration
├── dashboard.py        # Streamlit dashboard (main entry point)
└── README.md           # This file
```

## Troubleshooting

### Missing Credentials Error

If you see errors about missing credentials, ensure your `.env` file is properly configured with all required API keys.

### Kalshi Authentication Failed

If you don't have Kalshi API credentials, the demo will fall back to using sample topics. This is expected behavior and the demo will continue to run.

### News API Errors

- Ensure your NEWS_API_KEY is valid
- Free tier News API accounts have rate limits - if you see errors, wait a few minutes before retrying

### Azure OpenAI Errors

- Verify your Azure endpoint URL is correct (should end with `.openai.azure.com/`)
- Ensure your deployment name matches exactly with your Azure deployment
- Check that your API key is valid

## API References

- [Kalshi API Documentation](https://trading-api.readme.io/reference/getting-started)
- [News API Documentation](https://newsapi.org/docs)
- [Azure OpenAI Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/)


## Future Enhancements

Potential improvements for this dashboard:

- Add historical market price charts
- Export results to PDF/CSV format
- Integrate additional data sources (X/Twitter)
- Add real-time streaming updates
