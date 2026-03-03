"""
app.py - Streamlit Web Application
News Summarization Tool - Lab Work 3
Web interface for news retrieval and summarization.
"""

import streamlit as st
from news_retriever import NewsRetriever
from summarizer import NewsSummarizer
from user_manager import UserManager


def get_news_retriever(api_key):
    """Initialize NewsRetriever with the provided API key."""
    return NewsRetriever(api_key=api_key)

def get_summarizer(api_key):
    """Initialize NewsSummarizer with the provided API key."""
    return NewsSummarizer(api_key=api_key)

def rerun_app():
    """Rerun the Streamlit app (handles version compatibility)."""
    try:
        st.rerun()
    except AttributeError:
        st.experimental_rerun()


# Session state initialization
if "articles" not in st.session_state:
    st.session_state.articles = []

if "news_api_key" not in st.session_state:
    st.session_state.news_api_key = ""

if "groq_api_key" not in st.session_state:
    st.session_state.groq_api_key = ""

if "user_manager" not in st.session_state:
    st.session_state.user_manager = UserManager()

if "current_summary" not in st.session_state:
    st.session_state.current_summary = {}

if "search_performed" not in st.session_state:
    st.session_state.search_performed = False


# Page config
st.set_page_config(
    page_title="News Summarization Tool",
    page_icon=None,
    layout="wide"
)

# Sidebar
with st.sidebar:
    st.title("Settings")
    
    st.markdown("### API Keys")
    
    news_api_key = st.text_input(
        "NewsAPI Key:",
        type="password",
        value=st.session_state.news_api_key,
        help="Get free key at: https://newsapi.org/register"
    )
    if news_api_key:
        st.session_state.news_api_key = news_api_key

    groq_api_key = st.text_input(
        "Groq API Key:",
        type="password",
        value=st.session_state.groq_api_key,
        help="Get free key at: https://console.groq.com/keys"
    )
    if groq_api_key:
        st.session_state.groq_api_key = groq_api_key

    st.markdown("---")
    
    st.markdown("### Preferences")
    
    default_summary = st.radio(
        "Default Summary Type:",
        ["Brief", "Detailed"],
        index=0 if st.session_state.user_manager.get_summary_type() == "brief" else 1,
        horizontal=True
    )
    st.session_state.user_manager.set_summary_type(default_summary.lower())

    language = st.selectbox(
        "Summary Language:",
        ["English", "Arabic", "Spanish", "French", "German"]
    )
    st.session_state.user_manager.set_language(language)

    st.markdown("---")
    
    st.markdown("### Saved Topics")
    topics = st.session_state.user_manager.get_topics()
    
    if topics:
        for topic in topics:
            col1, col2 = st.columns([4, 1])
            col1.write(f"- {topic}")
            if col2.button("X", key=f"del_{topic}", help=f"Remove {topic}"):
                st.session_state.user_manager.remove_topic(topic)
                rerun_app()
    else:
        st.caption("No saved topics yet")

    with st.expander("Add New Topic"):
        new_topic = st.text_input("Topic name:", key="new_topic_input", label_visibility="collapsed")
        if st.button("Save Topic", use_container_width=True):
            if new_topic:
                st.session_state.user_manager.add_topic(new_topic)
                st.success(f"Saved: {new_topic}")
                rerun_app()

    st.markdown("---")
    
    st.markdown("### Recent Searches")
    history = st.session_state.user_manager.get_search_history(5)
    if history:
        for entry in history:
            st.caption(f"- {entry['query']} ({entry['results_count']})")
    else:
        st.caption("No search history")


# Main content
st.title("News Summarization Tool")
st.caption("Lab Work 3 - LangChain Application | Search news and get AI-powered summaries")

if not st.session_state.news_api_key or not st.session_state.groq_api_key:
    st.warning("Please enter both API keys in the sidebar to get started.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("""
        **NewsAPI Key (Free)**
        1. Visit [newsapi.org/register](https://newsapi.org/register)
        2. Create an account
        3. Copy your API key
        """)
    with col2:
        st.info("""
        **Groq API Key (Free)**
        1. Visit [console.groq.com/keys](https://console.groq.com/keys)
        2. Sign up / Log in
        3. Generate a new key
        """)
    st.stop()

st.markdown("---")

# Search section
col1, col2, col3 = st.columns([5, 1, 1])

with col1:
    search_query = st.text_input(
        "Search",
        placeholder="Enter a topic (e.g., artificial intelligence, climate change, sports...)",
        label_visibility="collapsed"
    )

with col2:
    num_articles = st.selectbox("Count", [5, 10, 15, 20], label_visibility="collapsed")

with col3:
    search_clicked = st.button("Search", type="primary", use_container_width=True)

# Quick search buttons
topics = st.session_state.user_manager.get_topics()
if topics:
    st.caption("Quick search from saved topics:")
    cols = st.columns(min(len(topics), 6))
    for i, topic in enumerate(topics[:6]):
        if cols[i].button(topic, key=f"quick_{topic}", use_container_width=True):
            search_query = topic
            search_clicked = True

# Perform search
if search_clicked and search_query:
    with st.spinner(f"Searching for '{search_query}'..."):
        try:
            retriever = get_news_retriever(st.session_state.news_api_key)
            articles = retriever.search_articles(search_query, page_size=num_articles)
            
            if articles:
                st.session_state.articles = articles
                st.session_state.user_manager.add_search(search_query, len(articles))
                st.session_state.search_performed = True
                st.session_state.current_summary = {}
                st.success(f"Found {len(articles)} articles about '{search_query}'")
            else:
                st.warning("No articles found. Try a different search term.")
                st.session_state.articles = []
        except Exception as e:
            st.error(f"Error: {str(e)}")

# Display articles
if st.session_state.articles:
    st.markdown("---")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader(f"Results ({len(st.session_state.articles)} articles)")
    with col2:
        if st.button("Summarize All", use_container_width=True):
            with st.spinner("Generating combined summary..."):
                try:
                    summarizer = get_summarizer(st.session_state.groq_api_key)
                    history = st.session_state.user_manager.get_search_history(1)
                    topic = history[0]['query'] if history else "news"
                    summary = summarizer.summarize_multiple_articles(
                        st.session_state.articles,
                        topic=topic
                    )
                    st.session_state.current_summary["all"] = summary
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    if "all" in st.session_state.current_summary:
        st.markdown("### Combined Summary")
        st.info(st.session_state.current_summary["all"])
        st.markdown("---")
    
    for i, article in enumerate(st.session_state.articles):
        with st.container():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"#### {i+1}. {article['title']}")
                
                meta_parts = []
                if article['source']:
                    meta_parts.append(f"Source: {article['source']}")
                if article['published_at']:
                    meta_parts.append(f"Date: {article['published_at'][:10]}")
                if article['author'] and article['author'] != 'Unknown':
                    meta_parts.append(f"Author: {article['author']}")
                
                st.caption(" | ".join(meta_parts))
            
            with col2:
                if st.button("Save Topic", key=f"save_{i}", use_container_width=True):
                    history = st.session_state.user_manager.get_search_history(1)
                    if history:
                        st.session_state.user_manager.add_topic(history[0]['query'])
                        st.toast(f"Saved topic: {history[0]['query']}")
            
            if article['description']:
                st.write(article['description'])
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("Brief Summary", key=f"brief_{i}", use_container_width=True):
                    with st.spinner("Generating..."):
                        try:
                            summarizer = get_summarizer(st.session_state.groq_api_key)
                            summary = summarizer.summarize_with_preferences(
                                article,
                                summary_type="brief",
                                language=st.session_state.user_manager.get_language()
                            )
                            st.session_state.current_summary[f"brief_{i}"] = summary
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
            
            with col2:
                if st.button("Detailed Summary", key=f"detailed_{i}", use_container_width=True):
                    with st.spinner("Generating..."):
                        try:
                            summarizer = get_summarizer(st.session_state.groq_api_key)
                            summary = summarizer.summarize_with_preferences(
                                article,
                                summary_type="detailed",
                                language=st.session_state.user_manager.get_language()
                            )
                            st.session_state.current_summary[f"detailed_{i}"] = summary
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
            
            with col3:
                st.link_button("Read Full Article", article['url'], use_container_width=True)
            
            if f"brief_{i}" in st.session_state.current_summary:
                st.success(f"**Brief Summary:** {st.session_state.current_summary[f'brief_{i}']}")
            
            if f"detailed_{i}" in st.session_state.current_summary:
                st.info(f"**Detailed Summary:** {st.session_state.current_summary[f'detailed_{i}']}")
            
            st.markdown("---")

# Empty state
if not st.session_state.articles and not st.session_state.search_performed:
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 3rem;">
            <h3>Start by searching for a topic</h3>
            <p>Enter any topic in the search bar above to find and summarize news articles.</p>
            <br>
            <p><strong>Try searching for:</strong></p>
            <p>Artificial Intelligence - Climate Change - Business - Sports</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
col1, col2, col3 = st.columns(3)
with col2:
    st.caption("Built with LangChain, Groq & Streamlit | Lab Work 3")
