"""
embedding_engine.py - Vector Embeddings Module
Creates and manages vector embeddings for news articles using
HuggingFace sentence-transformers and Chroma vector database.
"""

from typing import List, Dict
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
import os
import shutil


class EmbeddingEngine:
    """Creates and manages vector embeddings for news articles."""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize the EmbeddingEngine.
        
        Args:
            persist_directory: Directory to store the Chroma database
        """
        self.persist_directory = persist_directory
        
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )
        
        self.vectorstore = None
        self._initialize_vectorstore()
    
    def _initialize_vectorstore(self):
        """Initialize or load the Chroma vector store."""
        try:
            if os.path.exists(self.persist_directory):
                self.vectorstore = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embeddings
                )
            else:
                self.vectorstore = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embeddings
                )
        except Exception as e:
            print(f"Error initializing vector store: {e}")
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
    
    def add_articles(self, articles: List[Dict]) -> int:
        """
        Add articles to the vector store.
        
        Args:
            articles: List of article dictionaries from NewsRetriever
        
        Returns:
            Number of articles added
        """
        if not articles:
            return 0
        
        documents = []
        for article in articles:
            doc = Document(
                page_content=article.get("full_text", article.get("title", "")),
                metadata={
                    "title": article.get("title", ""),
                    "source": article.get("source", ""),
                    "url": article.get("url", ""),
                    "published_at": article.get("published_at", ""),
                    "author": article.get("author", ""),
                    "description": article.get("description", "")
                }
            )
            documents.append(doc)
        
        self.vectorstore.add_documents(documents)
        return len(documents)
    
    def search_similar(self, query: str, k: int = 5, filter_dict: Dict = None) -> List[Dict]:
        """
        Search for articles similar to the query.
        
        Args:
            query: Search query text
            k: Number of results to return
            filter_dict: Optional metadata filters
        
        Returns:
            List of similar articles with scores
        """
        if not self.vectorstore:
            return []
        
        try:
            results = self.vectorstore.similarity_search_with_score(
                query,
                k=k,
                filter=filter_dict
            )
            
            similar_articles = []
            for doc, score in results:
                article = {
                    "content": doc.page_content,
                    "title": doc.metadata.get("title", ""),
                    "source": doc.metadata.get("source", ""),
                    "url": doc.metadata.get("url", ""),
                    "published_at": doc.metadata.get("published_at", ""),
                    "description": doc.metadata.get("description", ""),
                    "similarity_score": float(score)
                }
                similar_articles.append(article)
            
            return similar_articles
            
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def get_article_count(self) -> int:
        """Get the number of articles in the vector store."""
        if not self.vectorstore:
            return 0
        try:
            return self.vectorstore._collection.count()
        except:
            return 0
    
    def clear_database(self):
        """Clear all articles from the vector store."""
        if os.path.exists(self.persist_directory):
            shutil.rmtree(self.persist_directory)
        self._initialize_vectorstore()
        print("Database cleared.")
    
    def get_all_articles(self, limit: int = 100) -> List[Dict]:
        """Get all articles from the vector store."""
        if not self.vectorstore:
            return []
        
        try:
            results = self.vectorstore.similarity_search("", k=limit)
            
            articles = []
            for doc in results:
                article = {
                    "content": doc.page_content,
                    "title": doc.metadata.get("title", ""),
                    "source": doc.metadata.get("source", ""),
                    "url": doc.metadata.get("url", ""),
                    "published_at": doc.metadata.get("published_at", ""),
                    "description": doc.metadata.get("description", "")
                }
                articles.append(article)
            
            return articles
            
        except Exception as e:
            print(f"Error getting articles: {e}")
            return []


if __name__ == "__main__":
    engine = EmbeddingEngine()
    
    print("Testing EmbeddingEngine")
    print("-" * 40)
    
    test_articles = [
        {
            "title": "AI Revolution in Healthcare",
            "description": "Artificial intelligence is transforming medical diagnosis",
            "full_text": "AI Revolution in Healthcare. Artificial intelligence is transforming medical diagnosis.",
            "source": "Tech News",
            "url": "https://example.com/ai-healthcare",
            "published_at": "2024-01-15"
        },
        {
            "title": "Climate Change Summit 2024",
            "description": "World leaders meet to discuss environmental policies",
            "full_text": "Climate Change Summit 2024. World leaders meet to discuss environmental policies.",
            "source": "World News",
            "url": "https://example.com/climate-summit",
            "published_at": "2024-01-14"
        }
    ]
    
    count = engine.add_articles(test_articles)
    print(f"Added {count} articles to the database")
    print(f"Total articles: {engine.get_article_count()}")
    
    print("\nSearching for 'machine learning in medicine'...")
    results = engine.search_similar("machine learning in medicine", k=2)
    
    for i, article in enumerate(results, 1):
        print(f"{i}. {article['title']} (score: {article['similarity_score']:.4f})")
