"""
user_manager.py - User Preferences Module
Manages user preferences and search history including:
- Saved topics of interest
- Search history
- Summary type preferences
- Language preferences
Data is stored in a JSON file for persistence.
"""

import json
import os
from datetime import datetime
from typing import List, Dict


class UserManager:
    """Manages user preferences and search history."""
    
    def __init__(self, data_file: str = "user_preferences.json"):
        """
        Initialize the UserManager.
        
        Args:
            data_file: Path to the JSON file for storing user data
        """
        self.data_file = data_file
        self.data = self._load_data()
    
    def _load_data(self) -> Dict:
        """Load user data from JSON file."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        return {
            "topics": [],
            "preferences": {
                "summary_type": "brief",
                "language": "English",
                "focus_areas": []
            },
            "search_history": []
        }
    
    def _save_data(self):
        """Save user data to JSON file."""
        try:
            with open(self.data_file, "w") as f:
                json.dump(self.data, f, indent=2)
        except IOError as e:
            print(f"Error saving data: {e}")
    
    def add_topic(self, topic: str) -> bool:
        """Add a topic to user's saved topics."""
        topic = topic.strip().lower()
        if topic and topic not in self.data["topics"]:
            self.data["topics"].append(topic)
            self._save_data()
            return True
        return False
    
    def remove_topic(self, topic: str) -> bool:
        """Remove a topic from user's saved topics."""
        topic = topic.strip().lower()
        if topic in self.data["topics"]:
            self.data["topics"].remove(topic)
            self._save_data()
            return True
        return False
    
    def get_topics(self) -> List[str]:
        """Get list of saved topics."""
        return self.data["topics"].copy()
    
    def clear_topics(self):
        """Clear all saved topics."""
        self.data["topics"] = []
        self._save_data()
    
    def set_summary_type(self, summary_type: str):
        """Set preferred summary type ('brief' or 'detailed')."""
        if summary_type in ["brief", "detailed"]:
            self.data["preferences"]["summary_type"] = summary_type
            self._save_data()
        else:
            raise ValueError("Summary type must be 'brief' or 'detailed'")
    
    def get_summary_type(self) -> str:
        """Get preferred summary type."""
        return self.data["preferences"].get("summary_type", "brief")
    
    def set_language(self, language: str):
        """Set preferred language for summaries."""
        self.data["preferences"]["language"] = language
        self._save_data()
    
    def get_language(self) -> str:
        """Get preferred language."""
        return self.data["preferences"].get("language", "English")
    
    def set_focus_areas(self, focus_areas: List[str]):
        """Set focus areas for personalized summaries."""
        self.data["preferences"]["focus_areas"] = [area.strip().lower() for area in focus_areas]
        self._save_data()
    
    def get_focus_areas(self) -> List[str]:
        """Get focus areas."""
        return self.data["preferences"].get("focus_areas", []).copy()
    
    def get_preferences(self) -> Dict:
        """Get all user preferences."""
        return self.data["preferences"].copy()
    
    def add_search(self, query: str, results_count: int = 0):
        """Add a search to history."""
        search_entry = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "results_count": results_count
        }
        self.data["search_history"].append(search_entry)
        
        if len(self.data["search_history"]) > 50:
            self.data["search_history"] = self.data["search_history"][-50:]
        
        self._save_data()
    
    def get_search_history(self, limit: int = 10) -> List[Dict]:
        """Get recent search history (most recent first)."""
        history = self.data["search_history"].copy()
        history.reverse()
        return history[:limit]
    
    def clear_search_history(self):
        """Clear all search history."""
        self.data["search_history"] = []
        self._save_data()
    
    def get_frequent_topics(self, limit: int = 5) -> List[str]:
        """Get most frequently searched topics."""
        topic_counts = {}
        for entry in self.data["search_history"]:
            query = entry["query"].lower()
            topic_counts[query] = topic_counts.get(query, 0) + 1
        
        sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
        return [topic for topic, count in sorted_topics[:limit]]
    
    def reset_all(self):
        """Reset all user data to defaults."""
        self.data = {
            "topics": [],
            "preferences": {
                "summary_type": "brief",
                "language": "English",
                "focus_areas": []
            },
            "search_history": []
        }
        self._save_data()
    
    def export_data(self) -> Dict:
        """Export all user data."""
        return self.data.copy()


if __name__ == "__main__":
    manager = UserManager("test_preferences.json")
    
    print("Testing UserManager")
    print("-" * 40)
    
    manager.add_topic("Technology")
    manager.add_topic("Sports")
    manager.add_topic("AI")
    print(f"Saved topics: {manager.get_topics()}")
    
    manager.set_summary_type("detailed")
    manager.set_language("English")
    manager.set_focus_areas(["business", "technology"])
    print(f"Preferences: {manager.get_preferences()}")
    
    manager.add_search("artificial intelligence", 10)
    manager.add_search("climate change", 5)
    print(f"Recent searches: {manager.get_search_history(3)}")
    print(f"Frequent topics: {manager.get_frequent_topics()}")
    
    os.remove("test_preferences.json")
    print("\nTest completed.")
