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

# Configure Streamlit page
st.set_page_config(
    page_title="Startup Analyzer", 
    page_icon="📊", 
    layout="wide"
)

# Load environment variables
load_dotenv()

# Configure OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

def fetch_enhanced_news():
    """
    Fetch news from multiple sources with image extraction
    """
    news_sources = [
        {
            'name': 'TechCrunch',
            'url': 'https://techcrunch.com/category/startups/feed/',
            'default_image': 'https://techcrunch.com/wp-content/uploads/2023/01/startup-tech-logo.jpg'
        },
        {
            'name': 'ISRO',
            'url': 'https://www.isro.gov.in/media/press-releases.rss',
            'default_image': 'https://www.isro.gov.in/sites/default/files/images/isro-logo.png'
        },
        {
            'name': 'NASA',
            'url': 'https://www.nasa.gov/rss/dyn/breaking_news.rss',
            'default_image': 'https://www.nasa.gov/sites/default/files/thumbnails/image/nasa-logo.png'
        }
    ]
    
    all_news = []
    
    for source in news_sources:
        try:
            feed = feedparser.parse(source['url'])
            
            for entry in feed.entries[:3]:  # Limit to 3 news items per source
                # Try to extract an image from the entry
                image_url = source['default_image']
                
                # Add some metadata
                news_item = {
                    'title': entry.title,
                    'link': entry.link,
                    'source': source['name'],
                    'published': entry.get('published', 'Recent'),
                    'description': entry.get('summary', 'No description available'),
                    'image': image_url
                }
                
                all_news.append(news_item)
        
        except Exception as e:
            st.error(f"Error fetching news from {source['name']}: {e}")
    
    return all_news

def extract_text(file):
    """
    Extract text from different file types
    """
    try:
        if file.type == "application/pdf":
            doc = fitz.open(stream=file.read(), filetype="pdf")
            return "\n".join([page.get_text("text") for page in doc])
        elif file.type == "application/vnd.openxmlformats-officedocument.presentationml.presentation":
            prs = Presentation(file)
            return "\n".join(["\n".join([shape.text for shape in slide.shapes if hasattr(shape, "text")]) for slide in prs.slides])
        else:
            image = Image.open(file)
            return pytesseract.image_to_string(image)
    except Exception as e:
        st.error(f"Error processing file: {e}")
        return ""

def main():
    """
    Main Streamlit application
    """
    # Application Title
    st.title("🚀 Startup Slide & Investor Analyzer")
    
    # Navigation Tabs
    tab1, tab2, tab3 = st.tabs(["📑 Slide Analyzer", "💰 Investor Matching", "📰 Startup News"])
    
    # Slide Analyzer Tab
    with tab1:
        st.header("AI Slide Analyzer")
        
        # User Inputs
        col1, col2 = st.columns(2)
        with col1:
            user_category = st.selectbox("Your Role", [
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
                extracted_text = extract_text(uploaded_file)
                
                # Perform AI Analysis
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
                    
                    # Display Analysis
                    analysis = response.choices[0].message.content
                    st.subheader("🔍 AI Insights")
                    st.info(analysis)
                
                except Exception as e:
                    st.error(f"AI Analysis Error: {e}")
    
    # Investor Matching Tab
    with tab2:
        st.header("Investor Matching")
        
        # Startup Details
        startup_idea = st.text_area("Describe Your Startup Concept")
        
        # Funding and Industry Selection
        col1, col2 = st.columns(2)
        with col1:
            funding_stage = st.selectbox("Funding Stage", [
                "Pre-Seed", "Seed", "Series A", 
                "Series B", "Growth Stage"
            ])
        
        with col2:
            industry = st.selectbox("Industry", [
                "Tech", "Healthcare", "Finance", 
                "E-commerce", "Deep Tech", 
                "Green Energy", "AI/ML"
            ])
        
        # Find Investors Button
        if st.button("Find Investors"):
            try:
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an expert startup investor matcher."},
                        {"role": "user", "content": f"""
                        Find top potential investors for a {industry} startup at {funding_stage} stage.
                        
                        Key Criteria:
                        - Relevant industry experience
                        - Stage-appropriate investment history
                        - Proven track record
                        - Geographic considerations
                        
                        Startup Concept: {startup_idea}
                        """}
                    ]
                )
                
                # Display Recommended Investors
                investors = response.choices[0].message.content
                st.subheader("🌟 Recommended Investors")
                st.success(investors)
            
            except Exception as e:
                st.error(f"Investor Matching Error: {e}")
    
    # Startup News Tab
    with tab3:
        st.header("Latest Startup & Space News")
        
        # Refresh News Button
        if st.button("Refresh News"):
            with st.spinner("Fetching latest news..."):
                news_data = fetch_enhanced_news()
                
                if news_data:
                    # Create a grid layout for news
                    for i in range(0, len(news_data), 3):
                        cols = st.columns(3)
                        
                        for j in range(3):
                            if i + j < len(news_data):
                                news_item = news_data[i + j]
                                
                                with cols[j]:
                                    # Display news card
                                    st.image(news_item['image'], use_column_width=True)
                                    st.markdown(f"### {news_item['title']}")
                                    st.markdown(f"**Source**: {news_item['source']}")
                                    st.markdown(f"**Published**: {news_item['published']}")
                                    st.markdown(f"*{news_item['description'][:100]}...*")
                                    st.markdown(f"[Read More]({news_item['link']})")
                
                else:
                    st.warning("Could not fetch news at the moment. Please try again later.")

    # Add some custom CSS for better styling

# Responsive CSS
st.markdown("""
<style>
@media (max-width: 768px) {
    .reportview-container .main .block-container {
        padding-top: 1rem;
        padding-right: 1rem;
        padding-left: 1rem;
        padding-bottom: 1rem;
    }
}
</style>
    """, unsafe_allow_html=True)

# Run the main application
if __name__ == "__main__":
    main()
