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
import streamlit as st

openai_api_key = st.secrets["OPENAI_API_KEY"]
openai.api_key = openai_api_key

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
            'name': 'NASA',
            'url': 'https://www.nasa.gov/rss/dyn/breaking_news.rss',
            'default_image': 'https://www.nasa.gov/sites/default/files/thumbnails/image/nasa-logo.png'
        }
    ]
    
    all_news = []
    
    for source in news_sources:
        try:
            feed = feedparser.parse(source['url'])
            
            for entry in feed.entries[:3]:
                image_url = source['default_image']
                
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
    st.title("🚀 Startup Slide & Investor Analyzer")
    
    tab1, tab2, tab3 = st.tabs(["📑 Slide Analyzer", "💰 Investor Matching", "📰 Startup News"])
    
    with tab1:
        st.header("AI Slide Analyzer")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            user_category = st.selectbox("Your Role", ["Student", "Educator", "Business Professional", "Startup Founder"])
        with col2:
            purpose = st.selectbox("Presentation Purpose", ["Business", "Academic", "Pitch", "Report"])
        with col3:
             desired_action = st.selectbox("What do you want to do with this content?", ["Summarize", "Extract Key Points", "Get AI Suggestions"])
            
        detail_level = st.slider(
            "Analysis Depth", 
            min_value=1, 
            max_value=10, 
            value=5, 
            help="1 = Basic overview, 10 = Comprehensive detailed analysis"
        )
        
        uploaded_file = st.file_uploader("Upload Presentation", type=["pptx", "pdf", "png", "jpg", "jpeg"])
        
        if uploaded_file:
            with st.spinner("Analyzing presentation..."):
                try:
                    extracted_text = extract_text(uploaded_file)
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a professional presentation analyzer."},
                            {"role": "user", "content": f"""
                            Analyze this presentation for {purpose}, user type {user_category}.
                            Provide constructive feedback on:
                            1. Content clarity
                            2. Structural effectiveness
                            3. Engagement potential
                            4. Areas of improvement
                            
                            Presentation Text:
                            {extracted_text}
                            """}
                        ]
                    )
                    feedback = response["choices"][0]["message"]["content"]
                    st.subheader("🔍 AI Analysis")
                    st.info(feedback)
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
    
    with tab3:
        st.header("📰 Latest Startup News")
        news_items = fetch_enhanced_news()
        
        if news_items:
            for news in news_items:
                with st.container():
                    st.markdown(
                        f"""
                        <div style="border-radius: 10px; border: 1px solid #ddd; padding: 15px; margin: 10px 0; background-color: #f9f9f9;">
                            <h3 style="color: #333;">{news['title']}</h3>
                            <img src="{news['image']}" style="width:100%; max-height:200px; object-fit:cover; border-radius:5px;" onerror="this.onerror=null; this.src='{news['image']}'" />
                            <p><strong>Source:</strong> {news['source']}</p>
                            <p><strong>Published:</strong> {news['published']}</p>
                            <p>{news['description'][:200]}...</p>
                            <a href="{news['link']}" target="_blank" style="color: #007bff; text-decoration: none;">Read more</a>
                        </div>
                        """, unsafe_allow_html=True
                    )
        else:
            st.warning("No news available at the moment. Please try again later.")
")

if __name__ == "__main__":
    main()
