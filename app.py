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

# Configure Streamlit page first - IMPORTANT
st.set_page_config(
    page_title="StartUp Analyzer", 
    page_icon="📊", 
    layout="wide"
)

# Load environment variables
load_dotenv()

# Configure OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

def fetch_startup_news():
    try:
        # Multiple news sources for comprehensive coverage
        news_sources = [
            # TechCrunch Startup News
            "https://techcrunch.com/category/startups/feed/",
            # Indian Space News
            "https://www.isro.gov.in/media/press-releases.rss",
            # Global Space News
            "https://www.nasa.gov/rss/dyn/breaking_news.rss"
        ]
        
        all_news = []
        for source in news_sources:
            feed = feedparser.parse(source)
            for entry in feed.entries[:5]:  # Limit to 5 news items per source
                all_news.append({
                    'title': entry.title,
                    'link': entry.link,
                    'source': feed.feed.title,
                    'published': entry.published
                })
        
        return all_news
    
    except Exception as e:
        st.error(f"Error fetching news: {e}")
        return []

def extract_text(file):
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
    # Title (after page config)
    st.title("📊 StartUp Slide & Investor Analyzer")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📑 Slide Analyzer", "💰 Investor Matching", "📰 Startup News"])
    
    # Slide Analyzer
    with tab1:
        st.header("AI Slide Analyzer")
        
        # User Inputs
        col1, col2 = st.columns(2)
        with col1:
            user_category = st.selectbox("Your Role", ["Student", "Educator", "Business Professional", "Startup Founder"])
        with col2:
            purpose = st.selectbox("Presentation Purpose", ["Business", "Academic", "Pitch", "Report"])
        
        # Detail Level Slider (Restored from original version)
        detail_level = st.slider("How detailed should the AI analysis be? (1 - Basic, 10 - In-depth)", 1, 10, 5)
        
        # Desired Action Dropdown (Restored from original version)
        desired_action = st.selectbox("What do you want to do with this content?", 
                                      ["Summarize", "Extract Key Points", "Get AI Suggestions", "Detailed Review"])
        
        # File Upload
        uploaded_file = st.file_uploader("Upload Presentation", type=["pptx", "pdf", "png", "jpg", "jpeg"])
        
        if uploaded_file:
            with st.spinner("Analyzing presentation..."):
                try:
                    # Safely extract text
                    extracted_text = extract_text(uploaded_file)
                    
                    # Use newer OpenAI API method
                    response = openai.chat.completions.create(
                        model="gpt-3.5-turbo",  
                        messages=[
                            {"role": "system", "content": "You are a professional presentation analyzer."},
                            {"role": "user", "content": f"""
                            Analyze this presentation for {purpose}, user type {user_category}, with detail level {detail_level}.
                            Specific Action: {desired_action}
                            
                            Provide comprehensive feedback considering:
                            1. Content clarity
                            2. Structural effectiveness
                            3. Engagement potential
                            4. Areas of improvement
                            5. Recommendations based on desired action
                            
                            Presentation Text:
                            {extracted_text}
                            """}
                        ]
                    )
                    
                    # Extract feedback
                    feedback = response.choices[0].message.content
                    
                    # Display Analysis
                    st.subheader("🔍 AI Analysis")
                    st.info(feedback)
                
                except Exception as e:
                    st.error(f"AI Analysis Error: {e}")
    
    # Investor Matching
    with tab2:
        st.header("Investor Matching")
        
        startup_idea = st.text_area("Describe Your Startup Concept")
        col1, col2 = st.columns(2)
        
        with col1:
            funding_stage = st.selectbox("Funding Stage", ["Pre-Seed", "Seed", "Series A", "Series B", "Growth Stage"])
        with col2:
            industry = st.selectbox("Industry", ["Tech", "Healthcare", "Finance", "E-commerce", "Deep Tech", "Green Energy", "AI/ML"])
        
        if st.button("Find Investors"):
            try:
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an expert startup investor matcher."},
                        {"role": "user", "content": f"""
                        Find top potential investors for a {industry} startup at {funding_stage} stage.
                        Key criteria:
                        - Relevant industry experience
                        - Stage-appropriate investment history
                        - Proven track record
                        - Geographic considerations
                        
                        Startup Concept: {startup_idea}
                        """}
                    ]
                )
                
                investors = response.choices[0].message.content
                st.subheader("🌟 Recommended Investors")
                st.success(investors)
            
            except Exception as e:
                st.error(f"Investor Matching Error: {e}")
    
    # Startup News
    with tab3:
        st.header("Latest Startup & Space News")
        
        if st.button("Refresh News"):
            with st.spinner("Fetching latest news..."):
                news_data = fetch_startup_news()
                
                if news_data:
                    # Create a DataFrame for better presentation
                    news_df = pd.DataFrame(news_data)
                    
                    for _, article in news_df.iterrows():
                        st.markdown(f"""
                        ### 📰 {article['title']}
                        **Source**: {article['source']}
                        **Published**: {article['published']}
                        [Read More]({article['link']})
                        ---
                        """)
                else:
                    st.warning("Could not fetch news at the moment. Please try again later.")

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

# Run the main function
if __name__ == "__main__":
    main()
