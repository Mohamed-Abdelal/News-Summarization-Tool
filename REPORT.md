# News Summarization Tool - Lab Work 3 Report

## Project Presentation Report

---

## Project Information

| Field | Details |
|-------|---------|
| Project Name | News Summarization Tool |
| Lab Work | Lab Work 3 |
| Course | AI-Based Applications with LangChain |
| Type | LangChain Application Development |

---

## Problem Statement

### Challenge
News consumption is overwhelming - hundreds of articles are published daily on any given topic. Readers need:
- Quick access to relevant news
- Ability to understand key points without reading full articles
- Personalized summaries based on their interests
- Organized tracking of topics they care about

### Solution
Build a News Summarization Application that:
1. Retrieves articles from NewsAPI based on user queries
2. Creates vector embeddings for semantic search
3. Generates personalized summaries (brief or detailed)
4. Tracks user preferences and search history

---

## Architecture

```
+----------------------------------------------------------+
|                     USER INTERFACE                        |
|            (Streamlit Web App / Command-Line)             |
+-----------------------------+----------------------------+
                              |
            +-----------------+-----------------+
            |                 |                 |
            v                 v                 v
+---------------+   +---------------+   +---------------+
|   NewsAPI     |   |   Groq LLM    |   |  Chroma DB    |
|   Retriever   |   |  Summarizer   |   |  Embeddings   |
+---------------+   +---------------+   +---------------+
            |                 |                 |
            +-----------------+-----------------+
                              |
                              v
                 +------------------------+
                 |     User Manager       |
                 |   (JSON Preferences)   |
                 +------------------------+
```

---

## Implementation Details

### 1. News Retrieval (news_retriever.py)

Purpose: Fetch articles from NewsAPI

```python
class NewsRetriever:
    BASE_URL = "https://newsapi.org/v2"
    
    def search_articles(self, query, language="en", sort_by="relevancy", page_size=10):
        endpoint = f"{self.BASE_URL}/everything"
        params = {
            "q": query,
            "language": language,
            "sortBy": sort_by,
            "pageSize": page_size,
            "apiKey": self.api_key
        }
        response = requests.get(endpoint, params=params)
        return self._process_articles(response.json().get("articles", []))
```

Features:
- Search by keyword with the /everything endpoint
- Get top headlines with /top-headlines
- Support for multiple languages and sort options

---

### 2. Vector Embeddings (embedding_engine.py)

Purpose: Create semantic embeddings for similarity search

```python
class EmbeddingEngine:
    def __init__(self, persist_directory="./chroma_db"):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )
        self.vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embeddings
        )
    
    def search_similar(self, query, k=5):
        results = self.vectorstore.similarity_search_with_score(query, k=k)
        return [{"title": doc.metadata["title"], "score": score} for doc, score in results]
```

Features:
- Uses HuggingFace all-MiniLM-L6-v2 model (free, no API key needed)
- Stores vectors in Chroma database
- Supports similarity search with scores

---

### 3. Summarization Chains (summarizer.py)

Purpose: Generate summaries using LangChain

**Chain 1: Brief Summary (1-2 sentences)**

```python
self.brief_template = PromptTemplate(
    template="""You are a news summarizer. Create a brief 1-2 sentence summary 
    of the following news article. Focus on the most important point only.

    Article:
    {text}

    Brief Summary (1-2 sentences):""",
    input_variables=["text"]
)
```

**Chain 2: Detailed Summary (paragraph)**

```python
self.detailed_template = PromptTemplate(
    template="""You are a professional news analyst. Create a comprehensive 
    summary of the following news article.
    Include:
    - Main topic and key points
    - Important details and context
    - Any significant implications

    Article:
    {text}

    Detailed Summary (one paragraph):""",
    input_variables=["text"]
)
```

---

### 4. User Preference Tracking (user_manager.py)

Purpose: Persist user settings and history

Data Structure:
```json
{
  "topics": ["technology", "sports", "AI"],
  "preferences": {
    "summary_type": "brief",
    "language": "English",
    "focus_areas": ["business", "technology"]
  },
  "search_history": [
    {
      "query": "artificial intelligence",
      "timestamp": "2024-01-15T10:30:00",
      "results_count": 10
    }
  ]
}
```

---

## Summary Types Comparison

| Aspect | Brief Summary | Detailed Summary |
|--------|---------------|------------------|
| Length | 1-2 sentences | Full paragraph |
| Focus | Single key point | Context + implications |
| Use Case | Scanning many articles quickly | Deep understanding |
| Token Usage | Lower (~50-100 tokens) | Higher (~200-400 tokens) |

---

## Requirements Checklist

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| NewsAPI integration | Done | news_retriever.py |
| Vector embeddings | Done | embedding_engine.py (HuggingFace) |
| Chroma/FAISS storage | Done | Chroma in embedding_engine.py |
| Two summarization chains | Done | Brief & Detailed in summarizer.py |
| User preference tracking | Done | JSON in user_manager.py |
| Command-line interface | Done | main.py |
| Web interface (bonus) | Done | app.py (Streamlit) |

---

## Required Files

| File | Purpose | Lines |
|------|---------|-------|
| news_retriever.py | NewsAPI requests | ~160 |
| embedding_engine.py | Vector embeddings | ~150 |
| summarizer.py | Summarization chains | ~150 |
| user_manager.py | Preferences tracking | ~170 |
| main.py | CLI application | ~250 |
| app.py | Streamlit web app | ~260 |

---

## Technologies Used

| Component | Technology | Purpose |
|-----------|------------|---------|
| LLM Framework | LangChain | Chain orchestration |
| LLM Provider | Groq (Llama 3.3 70B) | Fast, free inference |
| News API | NewsAPI | Article retrieval |
| Embeddings | HuggingFace (MiniLM) | Text vectorization |
| Vector DB | Chroma | Similarity search |
| Web UI | Streamlit | Interactive interface |
| Data Storage | JSON | User preferences |

---

## Demo Steps

### Web Interface Demo:

1. Run: `streamlit run app.py`
2. Enter API keys in sidebar
3. Search: "artificial intelligence"
4. Click "Brief Summary" on first article
5. Click "Detailed Summary" on same article
6. Click "Summarize All"
7. Save the topic
8. Show quick search with saved topic

### CLI Demo:

1. Run: `python main.py`
2. Select option 1 (Search)
3. Enter topic: "technology"
4. Summarize article #1
5. Select option 2 (View topics)
6. Select option 5 (View history)

---

## Conclusion

This project demonstrates:

1. API Integration - Real-time news retrieval from NewsAPI
2. Vector Search - Semantic similarity using embeddings
3. LLM Chains - Two distinct summarization approaches
4. User Experience - Both web and CLI interfaces
5. Persistence - User preferences saved across sessions

The application provides a practical example of building AI-powered tools with LangChain.

---

Lab Work 3 - News Summarization Tool
