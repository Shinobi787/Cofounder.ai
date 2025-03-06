import streamlit as st
import fitz  # PyMuPDF for PDFs
import pytesseract  # OCR for images
from pptx import Presentation
from PIL import Image
import openai
import requests
import os
import feedparser
import pandas as pd
import io
from datetime import datetime

# Configure Streamlit page
st.set_page_config(
    page_title="Startup Analyzer", 
    page_icon="📊", 
    layout="wide"
)

# Configure OpenAI API
openai_api_key = st.secrets["OPENAI_API_KEY"]
openai.api_key = openai_api_key

# Indian investors database
def load_indian_investors():
    """
    Load curated list of top Indian investors with their preferences
    """
    investors_data = {
        "Early Stage (Pre-Seed/Seed)": [
            {
                "name": "Blume Ventures",
                "focus": "Consumer Internet, Enterprise Software, Deep Tech",
                "typical_check": "$500K - $1.5M",
                "portfolio": "Unacademy, Dunzo, Purplle",
                "location": "Mumbai",
                "website": "https://blume.vc"
            },
            {
                "name": "Sequoia Surge",
                "focus": "Consumer, SaaS, FinTech, EdTech",
                "typical_check": "$1M - $2M",
                "portfolio": "CRED, Khatabook, Classplus",
                "location": "Bengaluru",
                "website": "https://www.sequoiacap.com/india/surge/"
            },
            {
                "name": "3one4 Capital",
                "focus": "SaaS, Enterprise, FinTech, Consumer",
                "typical_check": "$500K - $3M",
                "portfolio": "Licious, DarwinBox, Betterplace",
                "location": "Bengaluru",
                "website": "https://3one4capital.com/"
            },
            {
                "name": "Accel India",
                "focus": "SaaS, Consumer Tech, Healthcare",
                "typical_check": "$1M - $5M",
                "portfolio": "Flipkart, Freshworks, Swiggy",
                "location": "Bengaluru",
                "website": "https://www.accel.com/india"
            },
            {
                "name": "Kalaari Capital",
                "focus": "E-commerce, Health, Education",
                "typical_check": "$1M - $5M",
                "portfolio": "Urban Ladder, Myntra, Snapdeal",
                "location": "Bengaluru",
                "website": "https://www.kalaari.com/"
            }
        ],
        "Growth Stage (Series A/B)": [
            {
                "name": "Lightspeed India",
                "focus": "Consumer Tech, Enterprise, FinTech",
                "typical_check": "$5M - $20M",
                "portfolio": "OYO, Udaan, ShareChat",
                "location": "Delhi",
                "website": "https://lsvp.com/india/"
            },
            {
                "name": "Matrix Partners India",
                "focus": "Consumer Tech, FinTech, SaaS",
                "typical_check": "$5M - $25M",
                "portfolio": "Ola, Dailyhunt, Razorpay",
                "location": "Mumbai",
                "website": "https://www.matrixpartners.in/"
            },
            {
                "name": "Elevation Capital",
                "focus": "Consumer Internet, SaaS, FinTech",
                "typical_check": "$5M - $15M",
                "portfolio": "Paytm, Swiggy, Urban Company",
                "location": "Gurgaon",
                "website": "https://www.elevation.capital/"
            },
            {
                "name": "Nexus Venture Partners",
                "focus": "Enterprise, Consumer, Healthcare",
                "typical_check": "$2M - $10M",
                "portfolio": "Delhivery, Postman, Rapido",
                "location": "Mumbai",
                "website": "https://nexusvp.com/"
            },
            {
                "name": "Chiratae Ventures",
                "focus": "Consumer, Enterprise, Health, FinTech",
                "typical_check": "$2M - $15M",
                "portfolio": "Lenskart, PolicyBazaar, Cure.fit",
                "location": "Bengaluru",
                "website": "https://chiratae.com/"
            }
        ],
        "Late Stage (Series C+)": [
            {
                "name": "Peak XV Partners (formerly Sequoia India)",
                "focus": "Multi-sector",
                "typical_check": "$20M+",
                "portfolio": "BYJU'S, Zomato, Gojek",
                "location": "Bengaluru",
                "website": "https://www.peakxv.com/"
            },
            {
                "name": "Tiger Global",
                "focus": "Internet, Software, Consumer, FinTech",
                "typical_check": "$20M - $100M+",
                "portfolio": "Flipkart, BYJU'S, Razorpay",
                "location": "Global with India focus",
                "website": "https://www.tigerglobal.com/"
            },
            {
                "name": "SoftBank Vision Fund",
                "focus": "AI, Platform Businesses, Consumer Tech",
                "typical_check": "$100M+",
                "portfolio": "Paytm, OYO, Delhivery",
                "location": "Global with India office",
                "website": "https://thevisionfund.com/"
            },
            {
                "name": "Steadview Capital",
                "focus": "Consumer, FinTech, SaaS",
                "typical_check": "$20M - $100M",
                "portfolio": "Nykaa, Polygon, Zenoti",
                "location": "Hong Kong/India",
                "website": "https://www.steadview.com/"
            },
            {
                "name": "DST Global",
                "focus": "Internet Companies, Late Stage",
                "typical_check": "$50M+",
                "portfolio": "Swiggy, BYJU'S, Ola",
                "location": "Global with India investments",
                "website": "https://dst-global.com/"
            }
        ]
    }
    return investors_data

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
                
                # Try to download the image
                try:
                    response = requests.get(image_url)
                    image_data = response.content if response.status_code == 200 else None
                except:
                    image_data = None
                
                news_item = {
                    'title': entry.title,
                    'link': entry.link,
                    'source': source['name'],
                    'published': entry.get('published', 'Recent'),
                    'description': entry.get('summary', 'No description available'),
                    'image_url': image_url,
                    'image_data': image_data
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

def match_investors(startup_idea, industry, funding_stage):
    """
    Match startup to relevant investors based on database
    """
    investors_db = load_indian_investors()
    
    # Map user-selected funding stage to database categories
    stage_mapping = {
        "Pre-Seed": "Early Stage (Pre-Seed/Seed)",
        "Seed": "Early Stage (Pre-Seed/Seed)",
        "Series A": "Growth Stage (Series A/B)",
        "Series B": "Growth Stage (Series A/B)",
        "Growth Stage": "Late Stage (Series C+)"
    }
    
    # Get appropriate investor category
    matched_stage = stage_mapping.get(funding_stage, "Early Stage (Pre-Seed/Seed)")
    
    # Get investors for that stage
    relevant_investors = investors_db.get(matched_stage, [])
    
    # Optional: Use OpenAI to personalize recommendations based on startup idea
    if startup_idea.strip():
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert startup investor matcher."},
                    {"role": "user", "content": f"""
                    Analyze this startup idea in the {industry} industry at {funding_stage} stage:
                    
                    {startup_idea}
                    
                    Provide 3-5 most critical factors that would make this startup attractive to investors.
                    """} 
                ]
            )
            
            analysis = response.choices[0].message.content
        except:
            analysis = f"This {industry} startup at {funding_stage} stage would likely appeal to investors focused on innovation, market potential, and scalability."
    else:
        analysis = f"For a {industry} startup at {funding_stage} stage, these investors have a proven track record."
    
    return relevant_investors, analysis

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
    
    # Enhanced Investor Matching Tab
    with tab2:
        st.header("Investor Matching - India's Top Investors")
        
        # Startup Details
        startup_idea = st.text_area("Describe Your Startup Concept", height=150)
        
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
        if st.button("Find Matching Investors"):
            with st.spinner("Matching with top investors..."):
                matched_investors, analysis = match_investors(startup_idea, industry, funding_stage)
                
                # Display analysis
                st.subheader("🔍 Startup Analysis")
                st.write(analysis)
                
                # Display matched investors
                st.subheader("🌟 Top Recommended Investors")
                
                # Display investors in a more attractive format
                for i, investor in enumerate(matched_investors):
                    with st.expander(f"{i+1}. {investor['name']} - {investor['focus']}"):
                        col1, col2 = st.columns([1, 2])
                        with col1:
                            st.markdown(f"**Location:** {investor['location']}")
                            st.markdown(f"**Typical Investment:** {investor['typical_check']}")
                        with col2:
                            st.markdown(f"**Focus Areas:** {investor['focus']}")
                            st.markdown(f"**Notable Investments:** {investor['portfolio']}")
                            st.markdown(f"**Website:** [{investor['website']}]({investor['website']})")
    
    # Fixed News Tab
    with tab3:
        st.header("📰 Latest Startup News")
        
        # Refresh button
        if st.button("Refresh News"):
            st.experimental_rerun()
        
        news_items = fetch_enhanced_news()
        
        if news_items:
            # Create 3-column layout
            cols = st.columns(3)
            
            # Display news items in columns
            for i, news in enumerate(news_items):
                col = cols[i % 3]  # Distribute across columns
                
                with col:
                    st.subheader(news['title'])
                    
                    # Display image using Streamlit's native component
                    if news['image_data']:
                        try:
                            image = Image.open(io.BytesIO(news['image_data']))
                            st.image(image, use_container_width=True)
                        except Exception as e:
                            st.warning(f"Could not display image: {e}")
                            st.markdown(f"[Image Link]({news['image_url']})")
                    
                    st.markdown(f"**Source**: {news['source']}")
                    st.markdown(f"**Published**: {news['published']}")
                    
                    # Clean HTML from description
                    import re
                    description = re.sub('<.*?>', '', news['description'])
                    st.markdown(f"{description[:200]}...")
                    
                    st.markdown(f"[Read more]({news['link']})")
                    st.markdown("---")
        else:
            st.warning("No news available at the moment. Please try again later.")

if __name__ == "__main__":
    main()
