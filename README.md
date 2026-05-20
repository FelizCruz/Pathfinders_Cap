# Pathfinders Cap: AI-Powered Market Analysis Prototype

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![Azure AI](https://img.shields.io/badge/Azure_AI-0078D4?logo=microsoftazure&logoColor=white)](https://azure.microsoft.com/en-us/solutions/ai/)

## Project Overview

**Pathfinders Cap** is an advanced analytics prototype designed to bridge the gap between prediction market data and real-world news sentiment. By integrating Kalshi's market probabilities with real-time news from News API, the platform leverages Azure OpenAI (and GitHub Models) to perform semantic analysis, identifying hidden correlations and providing a data-driven outlook on future events.

The core mission is to substantiate event predictions with statistical sentiment data, offering a unified view of "what the market says" vs. "what the news reports."

---

## 🚀 Key Features

- **Predictive Market Integration**: Real-time data fetching from Kalshi API for various event categories (Politics, Economics, etc.).
- **Smart News Correlation**: Automated retrieval of relevant news articles based on market-leading outcomes.
- **AI-Powered Semantic Analysis**: Utilizes GPT-5 (via Azure OpenAI/GitHub Models) to interpret the relationship between market trends and media sentiment.
- **Interactive Visualization**: Dynamic Streamlit dashboard featuring probability pie charts and AI-generated insights.
- **Flexible Data Handling**: Support for multiple input modes including News API and upcoming X (Twitter) integration.

---

## 🛠️ Technical Stack

- **Frontend**: [Streamlit](https://streamlit.io/)
- **Language**: Python 3.8+
- **AI/LLM**: Azure OpenAI / GitHub Models (GPT-5 Chat)
- **Data APIs**: 
    - [Kalshi API](https://trading-api.readme.io/) (Prediction Markets)
    - [News API](https://newsapi.org/) (Global News)
- **Data Processing**: Pandas, Altair (Visualization)

---

## 📂 Project Structure

```text
Pathfinders_Cap/
├── src/
│   ├── demo1_kalshi_news/    # Main demo implementation
│   │   ├── dashboard.py       # Streamlit entry point
│   │   ├── kalshi_client.py   # Prediction market integration
│   │   ├── news_client.py     # News aggregation logic
│   │   └── azure_analyzer.py  # LLM & Sentiment analysis
│   └── Dashboard/             # Extended dashboard components
├── .env.example               # Template for credentials
└── requirements.txt           # Python dependencies
```

---

## 🚦 Getting Started

### 1. Prerequisites
- Python 3.8 or higher installed.
- API keys for **News API** and **Azure OpenAI** (or GitHub Models).
- (Optional) **Kalshi API** account for live market data.

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/FelizCruz/Pathfinders_Cap.git
cd Pathfinders_Cap

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration
1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and fill in your respective API keys for OpenAI, News API, and Kalshi.

### 4. Running the Demo
Launch the Streamlit dashboard from the root directory:
```bash
streamlit run src/demo1_kalshi_news/dashboard.py
```

---

## 🗺️ Roadmap

- [x] **Phase 1: Kalshi + News API Integration** (Current)
- [ ] **Phase 2: X (Twitter) Integration** - Real-time social sentiment analysis.
- [ ] **Phase 3: Multi-Format Export** - Unified PDF/DOC/CSV reporting.
- [ ] **Phase 4: Advanced Integrations**
    - Speech-to-Text (Voiced Transcripts)
    - Power BI Embedded Dashboards
    - Azure Event Hubs for real-time streaming

---

## 📝 Note on Integrations
Initially, the project focuses on the Kalshi + News API demo. Future iterations will explore the combination of social media (X) data and prediction markets to refine accuracy further.

---
*Last Updated: May 20, 2026*
