import streamlit as st
import os
import json
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv

from src.github_storage import GitHubStorage
from src.news_engine import fetch_rss_feeds, analyze_news_with_gemini
from src.ui_components import render_header, render_topic_card, render_sidebar_login, render_stats_chart

# Load environment variables
load_dotenv()

# Configuration
# Try to get secrets from Streamlit secrets first, then env vars
try:
    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
    REPO_NAME = st.secrets["REPO_NAME"]
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]
except:
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    REPO_NAME = os.getenv("REPO_NAME")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

st.set_page_config(page_title="My AI IT Newsroom", page_icon="📰", layout="wide")

# Initialize Storage
@st.cache_resource
def get_storage():
    if not GITHUB_TOKEN or not REPO_NAME:
        st.error("GitHub Credentials not found. Please check secrets/env.")
        return None
    return GitHubStorage(GITHUB_TOKEN, REPO_NAME)

storage = get_storage()

def load_data():
    if not storage:
        return {}, {}, [], {}
    
    news_data = storage.load_json("data/news_data.json") or {}
    stats_data = storage.load_json("data/stats.json") or {}
    feeds_data = storage.load_json("data/feeds.json") or []
    
    return news_data, stats_data, feeds_data

def save_news_data(news_data):
    if storage:
        storage.save_json("data/news_data.json", news_data, "Update news data")

def save_feeds_data(feeds_data):
    if storage:
        storage.save_json("data/feeds.json", feeds_data, "Update feeds list")

def update_stats(stats_data):
    today = datetime.now().strftime("%Y-%m-%d")
    current_count = stats_data.get(today, 0)
    stats_data[today] = current_count + 1
    if storage:
        storage.save_json("data/stats.json", stats_data, f"Update stats for {today}")
    return stats_data

# Main App Logic
def main():
    if not storage:
        return

    # Load Data
    news_data, stats_data, feeds_data = load_data()

    # Update Stats (Only on first load of session? Or every rerun? 
    # Ideally once per session, but streamlit reruns. Let's simplfy to just check if 'visited' in session state)
    if 'visited' not in st.session_state:
        stats_data = update_stats(stats_data)
        st.session_state['visited'] = True

    # Sidebar
    with st.sidebar:
        st.title("Settings")
        
        # Date Selection
        available_dates = sorted(news_data.keys(), reverse=True)
        selected_date = None
        if available_dates:
            selected_date = st.selectbox("Select Date", available_dates)
        
        st.markdown("---")
        
        # Admin Login
        input_password = render_sidebar_login()
        is_admin = input_password == ADMIN_PASSWORD

    # Admin Dashboard
    if is_admin:
        st.header("⚙️ Admin Dashboard")
        
        tab1, tab2 = st.tabs(["Feed Management", "Statistics"])
        
        with tab1:
            st.subheader("RSS Feeds")
            new_feed = st.text_input("Add New RSS Feed URL")
            if st.button("Add Feed"):
                if new_feed and new_feed not in feeds_data:
                    feeds_data.append(new_feed)
                    save_feeds_data(feeds_data)
                    st.success(f"Added {new_feed}")
                    st.rerun()
                elif new_feed in feeds_data:
                    st.warning("Feed already exists.")
            
            st.write("Current Feeds:")
            for feed in feeds_data:
                col1, col2 = st.columns([0.8, 0.2])
                col1.write(feed)
                if col2.button("Delete", key=feed):
                    feeds_data.remove(feed)
                    save_feeds_data(feeds_data)
                    st.rerun()
            
            st.markdown("---")
            st.subheader("Run Analysis")
            if st.button("🚀 Fetch & Analyze News"):
                with st.spinner("Fetching RSS feeds..."):
                    articles = fetch_rss_feeds(feeds_data)
                    st.info(f"Fetched {len(articles)} recent articles.")
                
                if articles:
                    with st.spinner("Analyzing with Gemini..."):
                        if not GEMINI_API_KEY:
                            st.error("Gemini API Key missing!")
                        else:
                            analysis_result = analyze_news_with_gemini(articles, GEMINI_API_KEY)
                            if analysis_result:
                                # Merge result into news_data
                                news_data.update(analysis_result)
                                save_news_data(news_data)
                                st.success("Analysis complete and saved!")
                                time.sleep(1) # Give a moment to see success
                                st.rerun()
                else:
                    st.warning("No recent articles found to analyze.")

        with tab2:
            render_stats_chart(stats_data)

    else:
        # Public View
        if selected_date and selected_date in news_data:
            report = news_data[selected_date]
            render_header(selected_date, report.get('briefing', 'No briefing available.'))
            
            topics = report.get('topics', [])
            for topic in topics:
                render_topic_card(topic)
        else:
            st.info("No news reports available. Admin needs to run analysis.")

if __name__ == "__main__":
    import time # imported here for button logic usage
    main()
