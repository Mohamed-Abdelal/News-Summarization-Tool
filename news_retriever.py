"""
news_retriever.py - NewsAPI Integration Module
Handles retrieving news articles from NewsAPI based on user queries.
Uses the 'everything' and 'top-headlines' endpoints.
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict
import os
from dotenv import load_dotenv

load_dotenv()


class NewsRetriever:
    """Retrieves news articles from NewsAPI."""
    
    BASE_URL = "https://newsapi.org/v2"
    
    def __init__(self, api_key: str = None):
        """
        Initialize the NewsRetriever.
        
        Args:
            api_key: NewsAPI key. If None, will try to load from environment.
        """
        self.api_key = api_key or os.getenv("NEWS_API_KEY")
        if not self.api_key:
            raise ValueError("NewsAPI key is required. Set NEWS_API_KEY in .env file.")
    
    def search_articles(
        self,
        query: str,
        language: str = "en",
        sort_by: str = "relevancy",
        page_size: int = 10,
        from_date: str = None,
        to_date: str = None
    ) -> List[Dict]:
        """
        Search for news articles using the 'everything' endpoint.
        
        Args:
            query: Search keywords or phrases
            language: Language code (e.g., 'en', 'ar', 'de')
            sort_by: Sort order ('relevancy', 'popularity', 'publishedAt')
            page_size: Number of articles to return (max 100)
            from_date: Start date (YYYY-MM-DD format)
            to_date: End date (YYYY-MM-DD format)
        
        Returns:
            List of article dictionaries
        """
        if not from_date:
            from_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        if not to_date:
            to_date = datetime.now().strftime("%Y-%m-%d")
        
        endpoint = f"{self.BASE_URL}/everything"
        
        params = {
            "q": query,
            "language": language,
            "sortBy": sort_by,
            "pageSize": page_size,
            "from": from_date,
            "to": to_date,
            "apiKey": self.api_key
        }
        
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "ok":
                articles = data.get("articles", [])
                return self._process_articles(articles)
            else:
                print(f"API Error: {data.get('message', 'Unknown error')}")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"Request Error: {e}")
            return []
    
    def get_top_headlines(
        self,
        country: str = "us",
        category: str = None,
        query: str = None,
        page_size: int = 10
    ) -> List[Dict]:
        """
        Get top headlines from NewsAPI.
        
        Args:
            country: Country code (e.g., 'us', 'gb', 'eg')
            category: News category ('business', 'technology', 'sports', etc.)
            query: Keywords to filter headlines
            page_size: Number of articles to return
        
        Returns:
            List of headline articles
        """
        endpoint = f"{self.BASE_URL}/top-headlines"
        
        params = {
            "country": country,
            "pageSize": page_size,
            "apiKey": self.api_key
        }
        
        if category:
            params["category"] = category
        if query:
            params["q"] = query
        
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "ok":
                articles = data.get("articles", [])
                return self._process_articles(articles)
            else:
                print(f"API Error: {data.get('message', 'Unknown error')}")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"Request Error: {e}")
            return []
    
    def _process_articles(self, articles: List[Dict]) -> List[Dict]:
        """Process and clean article data from API response."""
        processed = []
        
        for article in articles:
            if not article.get("title") or article.get("title") == "[Removed]":
                continue
            
            processed_article = {
                "title": article.get("title", "No Title"),
                "description": article.get("description", "No description available"),
                "content": article.get("content", article.get("description", "")),
                "url": article.get("url", ""),
                "source": article.get("source", {}).get("name", "Unknown"),
                "published_at": article.get("publishedAt", ""),
                "author": article.get("author", "Unknown"),
                "image_url": article.get("urlToImage", "")
            }
            
            processed_article["full_text"] = (
                f"{processed_article['title']}. "
                f"{processed_article['description']}. "
                f"{processed_article['content']}"
            )
            
            processed.append(processed_article)
        
        return processed
    
    def get_available_categories(self) -> List[str]:
        """Get list of available news categories."""
        return [
            "business",
            "entertainment", 
            "general",
            "health",
            "science",
            "sports",
            "technology"
        ]


if __name__ == "__main__":
    retriever = NewsRetriever()
    
    print("Testing NewsRetriever")
    print("-" * 40)
    
    articles = retriever.search_articles("artificial intelligence", page_size=3)
    
    print(f"Found {len(articles)} articles:\n")
    
    for i, article in enumerate(articles, 1):
        print(f"{i}. {article['title']}")
        print(f"   Source: {article['source']}")
        print(f"   Published: {article['published_at']}")
        print()
