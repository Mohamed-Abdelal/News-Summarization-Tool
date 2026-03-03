"""
summarizer.py - LangChain Summarization Module
Implements two types of summarization chains:
1. Brief Summary - 1-2 sentences capturing key points
2. Detailed Summary - Full paragraph with comprehensive information
"""

from typing import List, Dict
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain.schema import Document
import os
from dotenv import load_dotenv

load_dotenv()


class NewsSummarizer:
    """Generates summaries of news articles using LangChain and Groq."""
    
    def __init__(self, api_key: str = None):
        """
        Initialize the NewsSummarizer.
        
        Args:
            api_key: Groq API key. If None, will try to load from environment.
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("Groq API key is required. Set GROQ_API_KEY in .env file.")
        
        # Initialize Groq LLM
        self.llm = ChatGroq(
            model_name="llama-3.3-70b-versatile",
            temperature=0.3,  # Lower temperature for more focused summaries
            groq_api_key=self.api_key
        )
        
        # Create prompt templates for different summary types
        self._create_prompt_templates()
    
    def _create_prompt_templates(self):
        """Create prompt templates for brief and detailed summaries."""
        
        # Brief Summary Template (1-2 sentences)
        self.brief_template = PromptTemplate(
            template="""You are a news summarizer. Create a brief 1-2 sentence summary of the following news article.
Focus on the most important point only.

Article:
{text}

Brief Summary (1-2 sentences):""",
            input_variables=["text"]
        )
        
        # Detailed Summary Template (full paragraph)
        self.detailed_template = PromptTemplate(
            template="""You are a professional news analyst. Create a comprehensive summary of the following news article.
Include:
- Main topic and key points
- Important details and context
- Any significant implications

Article:
{text}

Detailed Summary (one paragraph):""",
            input_variables=["text"]
        )
        
        # Multiple Articles Summary Template
        self.multi_article_template = PromptTemplate(
            template="""You are a news analyst. Summarize the following collection of news articles about "{topic}".
Identify common themes and key points across all articles.

Articles:
{text}

Summary of all articles:""",
            input_variables=["text", "topic"]
        )
    
    def summarize_brief(self, article: Dict) -> str:
        """
        Generate a brief 1-2 sentence summary of an article.
        
        Args:
            article: Article dictionary with 'full_text' or 'content' key
        
        Returns:
            Brief summary string
        """
        text = article.get("full_text", article.get("content", article.get("description", "")))
        
        if not text:
            return "No content available to summarize."
        
        try:
            prompt = self.brief_template.format(text=text[:3000])  # Limit text length
            response = self.llm.invoke(prompt)
            return response.content.strip()
        except Exception as e:
            return f"Error generating summary: {str(e)}"
    
    def summarize_detailed(self, article: Dict) -> str:
        """
        Generate a detailed paragraph summary of an article.
        
        Args:
            article: Article dictionary with 'full_text' or 'content' key
        
        Returns:
            Detailed summary string
        """
        text = article.get("full_text", article.get("content", article.get("description", "")))
        
        if not text:
            return "No content available to summarize."
        
        try:
            prompt = self.detailed_template.format(text=text[:3000])  # Limit text length
            response = self.llm.invoke(prompt)
            return response.content.strip()
        except Exception as e:
            return f"Error generating summary: {str(e)}"
    
    def summarize_article(self, article: Dict, summary_type: str = "brief") -> str:
        """
        Generate a summary of an article based on the specified type.
        
        Args:
            article: Article dictionary
            summary_type: Either 'brief' or 'detailed'
        
        Returns:
            Summary string
        """
        if summary_type == "brief":
            return self.summarize_brief(article)
        elif summary_type == "detailed":
            return self.summarize_detailed(article)
        else:
            raise ValueError(f"Unknown summary type: {summary_type}. Use 'brief' or 'detailed'.")
    
    def summarize_multiple_articles(self, articles: List[Dict], topic: str = "news") -> str:
        """
        Generate a combined summary of multiple articles.
        
        Args:
            articles: List of article dictionaries
            topic: The topic of the articles
        
        Returns:
            Combined summary string
        """
        if not articles:
            return "No articles to summarize."
        
        # Combine article texts
        combined_text = ""
        for i, article in enumerate(articles[:5], 1):  # Limit to 5 articles
            title = article.get("title", f"Article {i}")
            content = article.get("full_text", article.get("content", article.get("description", "")))
            combined_text += f"\n--- Article {i}: {title} ---\n{content[:500]}\n"
        
        try:
            prompt = self.multi_article_template.format(text=combined_text, topic=topic)
            response = self.llm.invoke(prompt)
            return response.content.strip()
        except Exception as e:
            return f"Error generating summary: {str(e)}"
    
    def summarize_with_preferences(
        self,
        article: Dict,
        summary_type: str = "brief",
        focus_areas: List[str] = None,
        language: str = "English"
    ) -> str:
        """
        Generate a personalized summary based on user preferences.
        
        Args:
            article: Article dictionary
            summary_type: 'brief' or 'detailed'
            focus_areas: List of topics to focus on (e.g., ['technology', 'business'])
            language: Output language
        
        Returns:
            Personalized summary string
        """
        text = article.get("full_text", article.get("content", article.get("description", "")))
        
        if not text:
            return "No content available to summarize."
        
        # Build personalized prompt
        focus_instruction = ""
        if focus_areas:
            focus_instruction = f"Focus especially on aspects related to: {', '.join(focus_areas)}."
        
        length_instruction = "1-2 sentences" if summary_type == "brief" else "a detailed paragraph"
        
        prompt = f"""You are a news summarizer. Create a summary of the following article in {length_instruction}.
{focus_instruction}
Output the summary in {language}.

Article:
{text[:3000]}

Summary:"""
        
        try:
            response = self.llm.invoke(prompt)
            return response.content.strip()
        except Exception as e:
            return f"Error generating summary: {str(e)}"


if __name__ == "__main__":
    summarizer = NewsSummarizer()
    
    print("Testing NewsSummarizer")
    print("-" * 40)
    
    test_article = {
        "title": "AI Breakthrough in Medical Research",
        "full_text": """AI Breakthrough in Medical Research. Scientists at Stanford University have developed 
        a new artificial intelligence system that can detect early signs of cancer with 95% accuracy. 
        The AI analyzes medical imaging data and can identify tumors that human doctors might miss. 
        This breakthrough could save millions of lives by enabling earlier treatment."""
    }
    
    print("\nBrief Summary:")
    print(summarizer.summarize_brief(test_article))
    
    print("\nDetailed Summary:")
    print(summarizer.summarize_detailed(test_article))
