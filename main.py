"""
main.py - Command-Line Interface
News Summarization Tool - Lab Work 3
Main application for retrieving news articles and creating personalized summaries.
"""

from news_retriever import NewsRetriever
from embedding_engine import EmbeddingEngine
from summarizer import NewsSummarizer
from user_manager import UserManager
from dotenv import load_dotenv
import os

load_dotenv()


class NewsSummarizationApp:
    """Main application class for the News Summarization Tool."""
    
    def __init__(self):
        """Initialize all components: news retriever, embedding engine, summarizer, and user manager."""
        print("Initializing News Summarization Tool...")
        
        if not os.getenv("NEWS_API_KEY"):
            print("WARNING: NEWS_API_KEY not found in .env file")
        if not os.getenv("GROQ_API_KEY"):
            print("WARNING: GROQ_API_KEY not found in .env file")
        
        try:
            self.news_retriever = NewsRetriever()
            self.embedding_engine = EmbeddingEngine()
            self.summarizer = NewsSummarizer()
            self.user_manager = UserManager()
            print("All components initialized successfully.\n")
        except Exception as e:
            print(f"Initialization error: {e}")
            raise
    
    def search_news(self, query: str, count: int = 5) -> list:
        """Search for news articles and add to vector store."""
        print(f"\nSearching for news about '{query}'...")
        
        articles = self.news_retriever.search_articles(query, page_size=count)
        
        if articles:
            self.embedding_engine.add_articles(articles)
            self.user_manager.add_search(query, len(articles))
            print(f"Found {len(articles)} articles")
        else:
            print("No articles found")
        
        return articles
    
    def display_articles(self, articles: list):
        """Display article list."""
        if not articles:
            print("No articles to display.")
            return
        
        print("\n" + "=" * 60)
        for i, article in enumerate(articles, 1):
            print(f"\n{i}. {article['title']}")
            print(f"   Source: {article['source']}")
            print(f"   Date: {article['published_at'][:10] if article['published_at'] else 'N/A'}")
            print(f"   URL: {article['url'][:60]}...")
        print("\n" + "=" * 60)
    
    def summarize_article(self, article: dict, summary_type: str = None) -> str:
        """Generate summary for an article."""
        if summary_type is None:
            summary_type = self.user_manager.get_summary_type()
        
        preferences = self.user_manager.get_preferences()
        
        return self.summarizer.summarize_with_preferences(
            article,
            summary_type=summary_type,
            focus_areas=preferences.get("focus_areas"),
            language=preferences.get("language", "English")
        )
    
    def semantic_search(self, query: str, k: int = 5) -> list:
        """Search stored articles using semantic similarity."""
        return self.embedding_engine.search_similar(query, k=k)
    
    def run_cli(self):
        """Run the command-line interface."""
        print("\n" + "=" * 60)
        print("   News Summarization Tool")
        print("   Lab Work 3 - LangChain Application")
        print("=" * 60)
        
        while True:
            print("\nMain Menu:")
            print("1. Search for news")
            print("2. View saved topics")
            print("3. Search by saved topic")
            print("4. Semantic search (stored articles)")
            print("5. View search history")
            print("6. Settings")
            print("7. Exit")
            
            choice = input("\nEnter choice (1-7): ").strip()
            
            if choice == "1":
                self._search_news_menu()
            elif choice == "2":
                self._view_topics_menu()
            elif choice == "3":
                self._search_saved_topic_menu()
            elif choice == "4":
                self._semantic_search_menu()
            elif choice == "5":
                self._view_history_menu()
            elif choice == "6":
                self._settings_menu()
            elif choice == "7":
                print("\nGoodbye!")
                break
            else:
                print("Invalid choice. Please try again.")
    
    def _search_news_menu(self):
        """Handle news search."""
        query = input("\nEnter search topic: ").strip()
        if not query:
            print("Search cancelled.")
            return
        
        count = input("Number of articles (default 5): ").strip()
        count = int(count) if count.isdigit() else 5
        
        articles = self.search_news(query, count)
        
        if not articles:
            return
        
        self.display_articles(articles)
        
        save = input("\nSave this topic? (y/n): ").strip().lower()
        if save == "y":
            self.user_manager.add_topic(query)
            print(f"Topic '{query}' saved!")
        
        summarize = input("\nSummarize an article? (enter number or 'n'): ").strip()
        if summarize.isdigit():
            idx = int(summarize) - 1
            if 0 <= idx < len(articles):
                self._summarize_article_menu(articles[idx])
    
    def _summarize_article_menu(self, article: dict):
        """Handle article summarization."""
        print(f"\nSummarizing: {article['title'][:50]}...")
        print("\n1. Brief summary (1-2 sentences)")
        print("2. Detailed summary (paragraph)")
        print("3. Use my preference setting")
        
        choice = input("\nChoice: ").strip()
        
        if choice == "1":
            summary_type = "brief"
        elif choice == "2":
            summary_type = "detailed"
        else:
            summary_type = None
        
        print("\nGenerating summary...")
        summary = self.summarize_article(article, summary_type)
        
        print("\n" + "-" * 40)
        print("SUMMARY:")
        print("-" * 40)
        print(summary)
        print("-" * 40)
    
    def _view_topics_menu(self):
        """Display saved topics."""
        topics = self.user_manager.get_topics()
        
        if not topics:
            print("\nNo saved topics yet.")
            add = input("Add a topic? (y/n): ").strip().lower()
            if add == "y":
                topic = input("Enter topic: ").strip()
                if topic:
                    self.user_manager.add_topic(topic)
                    print(f"Topic '{topic}' saved!")
            return
        
        print("\nYour Saved Topics:")
        for i, topic in enumerate(topics, 1):
            print(f"{i}. {topic}")
        
        print("\n1. Add new topic")
        print("2. Remove topic")
        print("3. Back to menu")
        
        choice = input("\nChoice: ").strip()
        
        if choice == "1":
            topic = input("Enter new topic: ").strip()
            if topic:
                self.user_manager.add_topic(topic)
                print(f"Topic '{topic}' saved!")
        elif choice == "2":
            idx = input("Enter topic number to remove: ").strip()
            if idx.isdigit() and 0 < int(idx) <= len(topics):
                removed = topics[int(idx) - 1]
                self.user_manager.remove_topic(removed)
                print(f"Topic '{removed}' removed!")
    
    def _search_saved_topic_menu(self):
        """Search by saved topic."""
        topics = self.user_manager.get_topics()
        
        if not topics:
            print("\nNo saved topics. Add some first!")
            return
        
        print("\nSearch by Saved Topic:")
        for i, topic in enumerate(topics, 1):
            print(f"{i}. {topic}")
        
        choice = input("\nSelect topic number: ").strip()
        
        if choice.isdigit() and 0 < int(choice) <= len(topics):
            topic = topics[int(choice) - 1]
            articles = self.search_news(topic, 5)
            
            if articles:
                self.display_articles(articles)
                
                summarize = input("\nSummarize an article? (enter number or 'n'): ").strip()
                if summarize.isdigit():
                    idx = int(summarize) - 1
                    if 0 <= idx < len(articles):
                        self._summarize_article_menu(articles[idx])
    
    def _semantic_search_menu(self):
        """Handle semantic search in stored articles."""
        count = self.embedding_engine.get_article_count()
        
        if count == 0:
            print("\nNo articles stored yet. Search for news first!")
            return
        
        print(f"\nSemantic Search ({count} articles stored)")
        query = input("Enter search query: ").strip()
        
        if not query:
            return
        
        results = self.semantic_search(query, k=5)
        
        if not results:
            print("No matching articles found.")
            return
        
        print(f"\nFound {len(results)} similar articles:")
        print("-" * 40)
        
        for i, article in enumerate(results, 1):
            print(f"\n{i}. {article['title']}")
            print(f"   Similarity: {(1 - article['similarity_score']):.2%}")
            print(f"   Source: {article['source']}")
    
    def _view_history_menu(self):
        """Display search history."""
        history = self.user_manager.get_search_history(10)
        
        if not history:
            print("\nNo search history yet.")
            return
        
        print("\nRecent Searches:")
        for i, entry in enumerate(history, 1):
            print(f"{i}. '{entry['query']}' - {entry['results_count']} results")
            print(f"   {entry['timestamp'][:16]}")
        
        frequent = self.user_manager.get_frequent_topics(5)
        if frequent:
            print(f"\nMost searched: {', '.join(frequent)}")
    
    def _settings_menu(self):
        """Handle settings."""
        prefs = self.user_manager.get_preferences()
        
        print("\nSettings:")
        print(f"1. Summary type: {prefs['summary_type']}")
        print(f"2. Language: {prefs['language']}")
        print(f"3. Focus areas: {', '.join(prefs['focus_areas']) or 'None'}")
        print("4. Clear search history")
        print("5. Back to menu")
        
        choice = input("\nChoice: ").strip()
        
        if choice == "1":
            print("\n1. Brief (1-2 sentences)")
            print("2. Detailed (paragraph)")
            stype = input("Choice: ").strip()
            if stype == "1":
                self.user_manager.set_summary_type("brief")
            elif stype == "2":
                self.user_manager.set_summary_type("detailed")
            print("Setting updated!")
            
        elif choice == "2":
            lang = input("Enter preferred language: ").strip()
            if lang:
                self.user_manager.set_language(lang)
                print("Language updated!")
                
        elif choice == "3":
            areas = input("Enter focus areas (comma-separated): ").strip()
            if areas:
                self.user_manager.set_focus_areas([a.strip() for a in areas.split(",")])
                print("Focus areas updated!")
                
        elif choice == "4":
            confirm = input("Clear all history? (y/n): ").strip().lower()
            if confirm == "y":
                self.user_manager.clear_search_history()
                print("History cleared!")


if __name__ == "__main__":
    app = NewsSummarizationApp()
    app.run_cli()
