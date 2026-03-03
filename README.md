# News Summarization Tool

## Lab Work 3 - LangChain Application

A news summarization application using LangChain that retrieves articles on specific topics and creates concise summaries according to user preferences.

---

## Features

- **News Retrieval**: Fetch articles from NewsAPI on any topic
- **Vector Embeddings**: Store articles with semantic embeddings for similarity search
- **Two Summary Types**: Brief (1-2 sentences) and Detailed (full paragraph)
- **User Preferences**: Save topics, summary preferences, and search history
- **Multi-language Support**: Generate summaries in different languages
- **Dual Interface**: Web UI (Streamlit) and Command-line

---

## Project Structure

```
news_summarization_tool/
├── app.py                  # Streamlit web application
├── main.py                 # Command-line interface
├── news_retriever.py       # NewsAPI integration
├── embedding_engine.py     # Vector embeddings with Chroma
├── summarizer.py           # LangChain summarization chains
├── user_manager.py         # User preferences and history
├── requirements.txt        # Python dependencies
└── README.md               # Documentation
```

---

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/news-summarization-tool.git
cd news-summarization-tool
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure API Keys

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key_here
NEWS_API_KEY=your_newsapi_key_here
```

---

## API Keys

### NewsAPI (Free - 100 requests/day)

1. Visit: https://newsapi.org/register
2. Create a free account
3. Copy your API key

### Groq API (Free)

1. Visit: https://console.groq.com/keys
2. Sign up or log in
3. Generate a new API key

---

## Usage

### Web Interface (Streamlit)

```bash
streamlit run app.py
```

1. Enter your API keys in the sidebar
2. Type a search topic
3. Click Search to fetch articles
4. Click Brief Summary or Detailed Summary on any article
5. Use Summarize All for a combined summary

### Command-Line Interface

```bash
python main.py
```

Menu Options:
```
1. Search for news
2. View saved topics
3. Search by saved topic
4. Semantic search (stored articles)
5. View search history
6. Settings
7. Exit
```

---

## Code Documentation

### news_retriever.py

Handles API requests to NewsAPI.

```python
from news_retriever import NewsRetriever

retriever = NewsRetriever(api_key="your_key")
articles = retriever.search_articles("artificial intelligence", page_size=10)
headlines = retriever.get_top_headlines(country="us", category="technology")
```

### embedding_engine.py

Creates and manages vector embeddings using HuggingFace and Chroma.

```python
from embedding_engine import EmbeddingEngine

engine = EmbeddingEngine()
engine.add_articles(articles)
similar = engine.search_similar("machine learning", k=5)
```

### summarizer.py

Implements LangChain summarization with two chain types.

```python
from summarizer import NewsSummarizer

summarizer = NewsSummarizer(api_key="your_key")
brief = summarizer.summarize_brief(article)
detailed = summarizer.summarize_detailed(article)
```

### user_manager.py

Tracks user preferences and search history in JSON format.

```python
from user_manager import UserManager

manager = UserManager()
manager.add_topic("technology")
manager.set_summary_type("detailed")
manager.add_search("AI news", results_count=10)
```

---

## Deployment

### Deploy to Streamlit Cloud

1. Push to GitHub:
```bash
git init
git add .
git commit -m "News Summarization Tool"
git push -u origin main
```

2. Go to https://share.streamlit.io/
3. Connect your GitHub repository
4. Set main file: `app.py`
5. Deploy

---

## Technologies Used

| Technology | Purpose |
|------------|---------|
| LangChain | LLM application framework |
| Groq API | Fast LLM inference (Llama 3.3 70B) |
| NewsAPI | News article retrieval |
| Chroma | Vector database |
| HuggingFace | Sentence embeddings (all-MiniLM-L6-v2) |
| Streamlit | Web interface |

---

## Requirements Met

| Requirement | Implementation |
|-------------|----------------|
| NewsAPI retrieval | news_retriever.py |
| Vector embeddings | embedding_engine.py (HuggingFace) |
| Chroma storage | embedding_engine.py |
| Two summarization chains | summarizer.py (Brief & Detailed) |
| User preference tracking | user_manager.py (JSON) |
| Command-line interface | main.py |

---
