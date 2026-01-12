import streamlit as st

def render_header(date, briefing):
    """Renders the newspaper-style header."""
    st.markdown(f"# 📰 AI IT Newsroom - {date}")
    st.info(f"**Today's Briefing:** {briefing}")
    st.markdown("---")

def render_topic_card(topic):
    """Renders a single news topic card."""
    with st.container():
        st.subheader(f"📌 {topic['title']}")
        st.write(topic['content'])
        
        if 'links' in topic and topic['links']:
            with st.expander("Related Articles"):
                for link in topic['links']:
                    st.markdown(f"- [{link}]({link})")
        st.markdown("---")

def render_sidebar_login():
    """Renders the admin login form in sidebar."""
    st.sidebar.markdown("## Admin Login")
    password = st.sidebar.text_input("Password", type="password")
    return password

def render_stats_chart(stats_data):
    """Renders the visitor stats chart."""
    if not stats_data:
        st.warning("No stats available.")
        return
        
    st.subheader("Daily Visitor Statistics")
    st.line_chart(stats_data)
