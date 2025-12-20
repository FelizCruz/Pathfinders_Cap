"""
Streamlit Dashboard - Category-Driven Market Intelligence
User selects category → event → sees news + AI analysis
Run with: streamlit run src/demo1_kalshi_news/dashboard.py
"""
import streamlit as st
import pandas as pd
import altair as alt
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from demo1_kalshi_news.kalshi_client import KalshiClient
from demo1_kalshi_news.news_client import NewsClient
from demo1_kalshi_news.azure_analyzer import AzureAnalyzer

# Page config
st.set_page_config(page_title="Market Intelligence", page_icon="📊", layout="wide")

st.title("📊 Market Intelligence Dashboard")

# Initialize clients (cached)
@st.cache_resource
def get_clients():
    kalshi = KalshiClient()
    kalshi.login()
    return kalshi, NewsClient(), AzureAnalyzer()

kalshi, news, analyzer = get_clients()

# Cache events fetching
@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_all_events():
    """Fetch all events and organize by category."""
    events = kalshi.get_events(limit=200)
    return events

# Fetch all events
all_events = fetch_all_events()

# Get unique categories
categories = sorted(list(set(e.get('category', 'Other') for e in all_events if e.get('category'))))

# Step 1: Category Selection
st.markdown("### Step 1: Select a Category")
selected_category = st.selectbox(
    "Choose a prediction market category:",
    options=["-- Select a category --"] + categories,
    key="category_select"
)

if selected_category and selected_category != "-- Select a category --":
    # Filter events by category
    category_events = [e for e in all_events if e.get('category') == selected_category][:10]
    
    st.divider()
    
    # Step 2: Event Selection
    st.markdown(f"### Step 2: Select a Market Event ({selected_category})")
    
    if category_events:
        # Create event options
        event_options = {e.get('title', 'Unknown'): e for e in category_events}
        
        selected_event_title = st.selectbox(
            f"Top {len(category_events)} events in {selected_category}:",
            options=["-- Select an event --"] + list(event_options.keys()),
            key="event_select"
        )
        
        if selected_event_title and selected_event_title != "-- Select an event --":
            selected_event = event_options[selected_event_title]
            event_ticker = selected_event.get('event_ticker', selected_event.get('ticker', ''))
            
            st.divider()
            
            # Fetch market data for this event
            st.markdown("### Step 3: Market Data & Analysis")
            
            col1, col2 = st.columns(2)
            
            # Left column - Market Data with Pie Chart
            with col1:
                st.subheader("🎯 Prediction Market")
                
                # Display event info
                st.markdown(f"**{selected_event_title}**")
                st.caption(f"Category: {selected_category} | Ticker: `{event_ticker}`")
                
                # Fetch actual market data with prices
                with st.spinner("Fetching market data..."):
                    markets = kalshi.get_markets(event_ticker)
                
                # Prepare data for pie chart and analysis
                market_outcomes = []
                
                if markets and isinstance(markets, list) and len(markets) > 0:
                    # Check if this is a multi-outcome event (like elections)
                    if len(markets) > 1:
                        # Multiple mutually exclusive markets - show each outcome's YES probability
                        st.caption(f"📊 Multi-outcome event with {len(markets)} markets")
                        
                        for market in markets:
                            # Get market title/subtitle for the outcome name
                            outcome_name = market.get('yes_sub_title', 
                                          market.get('subtitle', 
                                          market.get('title', 'Unknown')))
                            
                            # Clean up the outcome name
                            if outcome_name and len(outcome_name) > 25:
                                outcome_name = outcome_name[:22] + "..."
                            
                            # Get yes probability - Kalshi returns prices in cents (0-100)
                            # Prefer yes_bid, fall back to last_price
                            yes_price = market.get('yes_bid') or market.get('last_price') or market.get('yes_ask') or 0
                            
                            # Convert to percentage (already in cents 0-100)
                            yes_pct = float(yes_price) if isinstance(yes_price, (int, float)) else 0
                            
                            if yes_pct > 0:  # Only include non-zero probabilities
                                market_outcomes.append({
                                    'name': outcome_name,
                                    'probability': yes_pct
                                })
                        
                        # Sort by probability descending
                        market_outcomes.sort(key=lambda x: x['probability'], reverse=True)
                        
                        # Create multi-outcome pie chart
                        if market_outcomes:
                            chart_data = pd.DataFrame({
                                'Outcome': [m['name'] for m in market_outcomes],
                                'Probability': [m['probability'] for m in market_outcomes]
                            })
                            
                            # Generate colors for multiple outcomes
                            colors = ['#28a745', '#dc3545', '#007bff', '#ffc107', '#6f42c1', 
                                     '#17a2b8', '#fd7e14', '#20c997', '#e83e8c', '#6c757d']
                            
                            pie_chart = alt.Chart(chart_data).mark_arc(innerRadius=40, outerRadius=80).encode(
                                theta=alt.Theta(field="Probability", type="quantitative"),
                                color=alt.Color(
                                    field="Outcome", 
                                    type="nominal",
                                    scale=alt.Scale(range=colors[:len(market_outcomes)]),
                                    legend=alt.Legend(title="Outcomes")
                                ),
                                tooltip=['Outcome', alt.Tooltip('Probability:Q', format='.1f')]
                            ).properties(width=280, height=280, title="Market Probabilities")
                            
                            st.altair_chart(pie_chart, use_container_width=False)
                            
                            # Display top outcomes as metrics
                            st.markdown("**Top Outcomes:**")
                            for i, outcome in enumerate(market_outcomes[:4]):
                                st.write(f"• {outcome['name']}: **{outcome['probability']:.1f}%**")
                            
                            # Store for AI analysis
                            yes_pct = market_outcomes[0]['probability'] if market_outcomes else 50
                            no_pct = 100 - yes_pct
                        else:
                            st.warning("No probability data found in markets")
                            yes_pct, no_pct = 50, 50
                    
                    else:
                        # Single market - show Yes/No pie chart
                        market = markets[0]
                        
                        # Get yes price - Kalshi returns prices in cents (0-100)
                        yes_price = market.get('yes_bid') or market.get('last_price') or market.get('yes_ask') or 0
                        
                        # Convert to percentage (already in cents 0-100)
                        yes_pct = float(yes_price) if isinstance(yes_price, (int, float)) and yes_price > 0 else 50
                        
                        no_pct = 100 - yes_pct
                        
                        # Create Yes/No pie chart
                        chart_data = pd.DataFrame({
                            'Vote': ['Yes ✅', 'No ❌'],
                            'Percentage': [yes_pct, no_pct]
                        })
                        
                        pie_chart = alt.Chart(chart_data).mark_arc(innerRadius=40, outerRadius=80).encode(
                            theta=alt.Theta(field="Percentage", type="quantitative"),
                            color=alt.Color(
                                field="Vote", 
                                type="nominal",
                                scale=alt.Scale(domain=['Yes ✅', 'No ❌'], range=['#28a745', '#dc3545']),
                                legend=alt.Legend(title="Outcome")
                            ),
                            tooltip=['Vote', alt.Tooltip('Percentage:Q', format='.1f')]
                        ).properties(width=250, height=250, title="Market Probability")
                        
                        st.altair_chart(pie_chart, use_container_width=False)
                        
                        # Display metrics
                        met_col1, met_col2 = st.columns(2)
                        with met_col1:
                            st.metric("✅ Yes", f"{yes_pct:.1f}%")
                        with met_col2:
                            st.metric("❌ No", f"{no_pct:.1f}%")
                    
                    # Additional market info
                    volume = market.get('volume', market.get('volume_24h', 'N/A'))
                    if volume != 'N/A':
                        st.metric("📊 Volume", f"{volume:,}" if isinstance(volume, int) else volume)
                else:
                    st.warning("Could not fetch detailed market data")
                    yes_pct = 50
                    no_pct = 50
            
            # Right column - News
            with col2:
                st.subheader("📰 Related News")
                
                # Build smarter search query based on event type
                if market_outcomes and len(market_outcomes) > 1:
                    # Multi-outcome event: search for top candidate + context
                    top_candidate = market_outcomes[0]['name']
                    # Add context from event title
                    if 'president' in selected_event_title.lower():
                        search_query = f"{top_candidate} president 2028"
                    elif 'pope' in selected_event_title.lower():
                        search_query = f"{top_candidate} pope"
                    elif 'election' in selected_event_title.lower():
                        search_query = f"{top_candidate} election"
                    else:
                        search_query = f"{top_candidate} {selected_category}"
                else:
                    # Single market: extract key terms from title
                    # Remove common filler words
                    query = selected_event_title
                    for word in ['Will ', 'Will the ', 'be ', '?', 'before ', 'in 2025', 'in 2026', 'in 2027', 'in 2028', 'in 2029']:
                        query = query.replace(word, ' ')
                    search_query = ' '.join(query.split())  # Clean up whitespace
                
                st.caption(f"🔍 Searching: *{search_query}*")
                
                with st.spinner(f"Fetching news..."):
                    articles = news.search_news(search_query, max_articles=5)
                
                if articles:
                    for article in articles:
                        title = article.get('title', 'No title')
                        source = article.get('source', {}).get('name', 'Unknown')
                        url = article.get('url', '#')
                        published = article.get('publishedAt', '')[:10]
                        
                        st.markdown(f"**[{title}]({url})**")
                        st.caption(f"📅 {published} | 🏢 {source}")
                        st.divider()
                else:
                    st.warning("No related news articles found")
                    articles = []
            
            # AI Analysis Section
            st.divider()
            st.markdown("### 🤖 AI Analysis")
            
            if st.button("Generate AI Insights", type="primary", use_container_width=True):
                with st.spinner("GPT-5 is analyzing market data and news..."):
                    # Prepare market data summary based on single vs multi-outcome
                    if market_outcomes:
                        # Multi-outcome event
                        market_summary = f"PREDICTION MARKET: {selected_event_title}\n"
                        market_summary += f"Category: {selected_category}\n"
                        market_summary += f"Type: Multi-outcome event with {len(market_outcomes)} possible outcomes\n\n"
                        market_summary += "OUTCOME PROBABILITIES:\n"
                        for outcome in market_outcomes:
                            market_summary += f"- {outcome['name']}: {outcome['probability']:.1f}%\n"
                        market_summary += f"\nThe leading outcome is '{market_outcomes[0]['name']}' at {market_outcomes[0]['probability']:.1f}%."
                    else:
                        # Single Yes/No market
                        market_summary = f"""PREDICTION MARKET: {selected_event_title}
Category: {selected_category}
Type: Binary Yes/No market

MARKET PROBABILITIES:
- Yes: {yes_pct:.1f}%
- No: {no_pct:.1f}%

This means the market currently predicts a {yes_pct:.1f}% chance of "Yes" outcome."""
                    
                    # Prepare news summary
                    news_summary = f"NEWS ARTICLES RELATED TO '{selected_event_title}':\n\n"
                    if articles:
                        for i, article in enumerate(articles, 1):
                            news_summary += f"{i}. {article.get('title', 'No title')}\n"
                            news_summary += f"   Source: {article.get('source', {}).get('name', 'Unknown')}\n"
                            desc = article.get('description', '')
                            if desc:
                                news_summary += f"   Summary: {desc[:250]}\n"
                            news_summary += "\n"
                    else:
                        news_summary += "No relevant news articles found.\n"
                    
                    # Call AI with specific prompt - include full market context
                    analysis = analyzer.analyze_event_with_news(
                        event_title=selected_event_title,
                        yes_pct=yes_pct,
                        no_pct=no_pct,
                        news_summary=news_summary,
                        market_summary=market_summary
                    )
                
                st.success("Analysis complete!")
                st.markdown(analysis)
                # Instruct GPT-5 to end the response and not ask follow-up questions
                st.caption("GPT-5 will not ask follow-up questions. Analysis ends here.")
    else:
        st.warning(f"No events found in category: {selected_category}")

else:
    # Show intro when no category selected
    st.info("👆 Select a category above to explore prediction markets!")
    
    # Show category overview
    st.markdown("### 📊 Available Categories")
    
    # Count events per category
    category_counts = {}
    for e in all_events:
        cat = e.get('category', 'Other')
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    # Display as columns
    cols = st.columns(4)
    for i, (cat, count) in enumerate(sorted(category_counts.items(), key=lambda x: -x[1])):
        with cols[i % 4]:
            st.metric(cat, f"{count} events")

# Footer
st.divider()
st.caption("Powered by Kalshi API, NewsAPI, and GPT-5")
