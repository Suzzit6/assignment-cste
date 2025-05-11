# Amazon & YouTube Data Tools

This repository contains two separate tools:

1. [Amazon Scraper](#amazon-scraper) - A Selenium-based scraper for extracting sponsored product data from Amazon.
2. [YouTube Video Analyzer](#youtube-video-analyzer) - A Streamlit application that finds and recommends the most relevant YouTube videos based on a search query.

## Amazon Scraper

### Overview

The Amazon Scraper tool uses Selenium to scrape sponsored product information from Amazon's search results. It specifically targets the "soft toys" category and extracts details like:

- Product title
- Brand name
- Price
- Rating
- Number of reviews
- Product image URL
- Product page URL

### Files

- [amazon_sponsored_softtoys.csv](amazon-scraper/amazon_sponsored_softtoys.csv) - CSV file containing the scraped data
- [app.py](amazon-scraper/app.py) - The main Python script for scraping Amazon
- [analysis.ipynb](amazon-scraper/analysis.ipynb) - Jupyter notebook for analyzing the scraped data

### Setup & Installation

1. Install the required packages:
   ```bash
   pip install selenium pandas webdriver-manager
   ```

2. Run the scraper:
   ```bash
   cd amazon-scraper
   python app.py
   ```

### Features

- Headless browser operation for faster scraping
- Detailed product information extraction
- Brand detection from product pages
- CSV output for easy data analysis

## YouTube Video Analyzer

### Overview

The YouTube Video Analyzer is a Streamlit application that helps users find the most relevant YouTube videos based on their search query. It uses:

- YouTube Data API for searching videos
- Google Speech Recognition for voice input
- Google's Gemini AI for analyzing video relevancy

### Files

- [app.py](youtube-assignment/app.py) - Main Streamlit application
- [requirements.txt](youtube-assignment/requirements.txt) - Required Python packages
- [.env](youtube-assignment/.env) - Environment variables for API keys (not included in repository)

### Setup & Installation

1. Install the required packages:
   ```bash
   cd youtube-assignment
   pip install -r requirements.txt
   ```

2. Create a `.env` file with your API keys:
   ```
   YOUTUBE_API_KEY=your_youtube_api_key
   GOOGLE_API_KEY=your_google_api_key
   ```

3. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```

### Features

- Search for YouTube videos published in the last 14 days
- Filter videos by duration (4-20 minutes)
- Voice input for search queries
- AI-powered video relevance ranking
- Embedded video player for the most relevant result

## Security Note

API keys have been included in the repository files. In a production environment, these should be removed from the code and stored securely as environment variables or in a secure vault.

## Requirements

### Amazon Scraper
- Python 3.7+
- Selenium
- Pandas
- Webdriver-manager

### YouTube Analyzer
- Python 3.7+
- Streamlit
- Google API Python Client
- Google Generative AI
- Speech Recognition
- PyAudio
- isodate