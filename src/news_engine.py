import feedparser
import google.generativeai as genai
import json
from datetime import datetime, timedelta
import dateutil.parser
import streamlit as st
import time

def fetch_rss_feeds(feed_urls):
    """
    Fetches and filters news articles from RSS feeds (last 3 days).
    """
    articles = []
    three_days_ago = datetime.now() - timedelta(days=3)
    
    for url in feed_urls:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                # Try to parse published date
                published_time = None
                if 'published' in entry:
                    try:
                        published_time = dateutil.parser.parse(entry.published)
                        # Make timezone-naive for comparison if needed, or handle timezone
                        if published_time.tzinfo is not None:
                             published_time = published_time.replace(tzinfo=None) # Simplify for prototype
                    except:
                        pass
                
                # If no date found, default to now (or skip? let's include for safety if recent check fails)
                # But specification says "last 3 days", so we should try to filter.
                # If parsing fails, maybe we skip or include. Let's include if date is missing but warn?
                # For robustness, if date parsing fails, we skip to avoid garbage.
                
                if published_time and published_time >= three_days_ago:
                    articles.append({
                        'title': entry.get('title', 'No Title'),
                        'link': entry.get('link', ''),
                        'summary': entry.get('summary', ''),
                        'published': entry.get('published', str(datetime.now()))
                    })
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            continue
            
    return articles

def analyze_news_with_gemini(articles, api_key):
    """
    Analyzes articles using Gemini API to produce a daily briefing.
    """
    if not articles:
        return None

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-pro')

    # Prepare data for prompt
    articles_text = ""
    for idx, art in enumerate(articles[:50]): # Limit to 50 articles to avoid context limit issues if too many
        articles_text += f"{idx+1}. Title: {art['title']}\nSummary: {art['summary']}\nLink: {art['link']}\nDate: {art['published']}\n\n"

    today_str = datetime.now().strftime("%Y-%m-%d")
    
    prompt = f"""
    You are an expert IT journalist. Analyze the following news articles collected on {today_str}.
    
    Tasks:
    1. Summarize the overall IT trend/briefing for today.
    2. Group similar articles into topics.
    3. For each topic, provide a title, a detailed analysis content, and a list of related original links.
    
    Output strictly in the following JSON format (no markdown code blocks, just raw JSON):
    {{
      "{today_str}": {{
        "briefing": "Overall summary of today's IT news trends...",
        "topics": [
          {{
            "title": "Topic Title",
            "content": "Detailed analysis of this topic...",
            "links": ["http://link1...", "http://link2..."]
          }}
        ]
      }}
    }}
    
    Articles:
    {articles_text}
    """

    try:
        response = model.generate_content(prompt)
        # Cleanup response if it contains markdown ticks
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
            
        return json.loads(text)
    except Exception as e:
        st.error(f"Error during Gemini analysis: {e}")
        return None
