# Pathfinders Cap

## Project Overview

Initially, we are going to focus on a simple demo and then later think about adding integrations in this order: Speech (Voiced Transcripts), Power BI, Event Hubs.

## Demo

### Part 1: Input Preprocessing

We have two modes for input preprocessing:

1. **Kalshi API data + News API data**

2. **Kalshi API data + X (formerly Twitter) data**

*[Note: We may or may not combine this later, but for simplicity, we'll keep them separate initially.]*

After this step, we can compose the combined data as a unified PDF/DOC/CSV or perhaps two separate documents for Kalshi and X data that reference similar topics (e.g., who is favored to win the next election).

### Part 2: AI Operations

Here, we will perform AI operations on the data composed from Part 1.

- Use semantic analysis and key phrase extraction to gauge the general direction of people's opinions.

- Use the Grok endpoint to interpret the opinion data and how it measures up against the event prediction data from Kalshi.

This aims to improve and substantiate predictions of future events with actual statistical data.

Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): 2025-12-10 08:26:12
Current User's Login: FelizCruz