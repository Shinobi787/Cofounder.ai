import streamlit as st
import fitz  # PyMuPDF for PDFs
import pytesseract  # OCR for images
from pptx import Presentation
from PIL import Image
import openai
import requests
import os
from dotenv import load_dotenv
import feedparser
import pandas as pd
import logging
from typing import List, Dict, Any

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# API Configuration
class APIConfig:
    """Centralized configuration for API management"""
    @staticmethod
    def configure_openai():
        """Configure OpenAI API with error handling"""
        try:
            load_dotenv()  # Load environment variables
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API Key not found in environment variables")
            openai.api_key = api_key
        except Exception as e:
            st.error(f"API Configuration Error: {e}")
            logger.error(f"OpenAI API Configuration Failed: {e}")

# News Management
class NewsManager:
    """Advanced news fetching and management"""
    @staticmethod
    def fetch_enhanced_news() -> List[Dict[str, Any]]:
        """
        Fetch comprehensive news from multiple sources with robust error handling
        
        Returns:
            List of news dictionaries with enhanced information
        """
        news_sources = [
            {
                'name': 'TechCrunch Startups',
                'url': 'https://techcrunch.com/category/startups/feed/',
                'fallback_image': 'https://techcrunch.com/wp-content/uploads/2023/01/startup-icon.png'
            },
            {
                'name': 'ISRO News',
                'url': 'https://www.isro.gov.in/media/press-releases.rss',
                'fallback_image': 'https://www.isro.gov.in/sites/default/files/images/isro-logo.png'
            },
            {
                'name': 'NASA Breaking News',
                'url': 'https://www.nasa.gov/rss/dyn/breaking_news.rss',
                'fallback_image': 'https://www.nasa.gov/sites/default/files/thumbnails/image/nasa-logo.png'
            }
        ]
        
        all_news = []
        
        for source in news_sources:
            try:
                feed = feedparser.parse(source['url'])
                
                for entry in feed.entries[:3]:  # Limit entries per source
                    news_item = {
                        'title': entry.title,
                        'link': entry.link,
                        'source': source['name'],
                        'published': entry.get('published', 'Unknown Date'),
                        'image': source['fallback_image']
                    }
                    all_news.append(news_item)
                
            except Exception as e:
                logger.error(f"Error fetching news from {source['name']}: {e}")
        
        return all_news

# Text Extraction Utility
class TextExtractor:
    """Advanced text extraction from various file types"""
    @staticmethod
    def extract_text(uploaded_file) -> str:
        """
        Extract text from different file types with comprehensive error handling
        
        Args:
            uploaded_file: Streamlit uploaded file object
        
        Returns:
            Extracted text or empty string
        """
        try:
            if uploaded_file.type == "application/pdf":
                doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                return "\n".join([page.get_text("text") for page in doc])
            
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.presentationml.presentation":
                prs = Presentation(uploaded_file)
                return "\n".join([
                    "\n".join([shape.text for shape in slide.shapes if hasattr(shape, "text")])
                    for slide in prs.slides
                ])
            
            elif uploaded_file.type in ["image/png", "image/jpeg", "image/jpg"]:
                image = Image.open(uploaded_file)
                return pytesseract.image_to_string(image)
            
            else:
                st.warning(f"Unsupported file type: {uploaded_file.type}")
                return ""
        
        except Exception as e:
            st.error(f"Text Extraction Error: {e}")
            logger.error(f"Text Extraction Failed: {e}")
            return ""

# AI Analysis Services
class AIAnalysisService:
    """Centralized AI-powered analysis services"""
    @staticmethod
    def analyze_presentation(extracted_text: str, purpose: str, user_category: str, detail_level: int) -> str:
        """
        Perform AI-powered presentation analysis
        
        Args:
            extracted_text: Text content of the presentation
            purpose: Presentation purpose
            user_category: User's professional category
            detail_level: Depth of analysis
        
        Returns:
            AI-generated analysis
        """
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional presentation analyzer."},
                    {"role": "user", "content": f"""
                    Analyze this presentation for {purpose}, user type {user_category}, 
                    with detail level {detail_level}.
                    
                    Provide comprehensive, constructive feedback:
                    1. Content Clarity
                    2. Structural Effectiveness
                    3. Engagement Potential
                    4. Areas of Improvement
                    5. Actionable Recommendations
                    
                    Presentation Content:
                    {extracted_text}
                    """}
                ]
            )
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"AI Analysis Failed: {e}")
            st.error("AI Analysis encountered an error. Please try again.")
            return "Analysis could not be completed."

def main():
    """Main Streamlit application entry point"""
    # Page Configuration
    st.set_page_config(
        page_title="Startup Analyzer", 
        page_icon="📊", 
        layout="wide"
    )
    
    # Initialize API Configuration
    APIConfig.configure_openai()
    
    # Application Title
    st.title("🚀 Startup Slide & Investor Analyzer")
    
    # Navigation Tabs
    tab1, tab2, tab3 = st.tabs([
        "📑 Slide Analyzer", 
        "💰 Investor Matching", 
        "📰 Startup News"
    ])
    
    # Slide Analyzer Tab
    with tab1:
        st.header("AI Presentation Analysis")
        
        # User Inputs
        col1, col2 = st.columns(2)
        with col1:
            user_category = st.selectbox("Your Professional Role", [
                "Student", "Educator", "Business Professional", 
                "Startup Founder", "Researcher"
            ])
        
        with col2:
            purpose = st.selectbox("Presentation Purpose", [
                "Business Pitch", "Academic Presentation", 
                "Investor Deck", "Training", "Research Proposal"
            ])
        
        # Analysis Configuration
        detail_level = st.slider(
            "Analysis Depth", 
            min_value=1, 
            max_value=10, 
            value=5, 
            help="1 = Basic overview, 10 = Comprehensive detailed analysis"
        )
        
        # File Upload
        uploaded_file = st.file_uploader(
            "Upload Presentation", 
            type=["pptx", "pdf", "png", "jpg", "jpeg"],
            help="Supported formats: PowerPoint, PDF, Images"
        )
        
        if uploaded_file:
            with st.spinner("Analyzing your presentation..."):
                # Extract Text
                extracted_text = TextExtractor.extract_text(uploaded_file)
                
                # Perform AI Analysis
                analysis = AIAnalysisService.analyze_presentation(
                    extracted_text, purpose, user_category, detail_level
                )
                
                # Display Analysis
                st.subheader("🔍 AI Insights")
                st.info(analysis)
    
    # Remaining tabs would follow similar modular design
    # ... (code for other tabs remains similar)

if __name__ == "__main__":
    main()
