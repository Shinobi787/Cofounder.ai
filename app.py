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

# Configure Streamlit page with better layout and colors
st.set_page_config(
    page_title="cofounder.ai - Startup Intelligence Platform", 
    page_icon="🚀", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS for better styling
st.markdown("""
<style>
    /* Main styling */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Header styling */
    .st-emotion-cache-10trblm {
        color: #2c3e50;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #f8f9fa;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e9ecef;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #2c3e50;
        color: white;
    }
    
    /* Button styling */
    .stButton>button {
        background-color: #2c3e50;
        color: white;
        border-radius: 8px;
        padding: 8px 16px;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #1a252f;
        color: white;
    }
    
    /* Card styling for news */
    .news-card {
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        padding: 15px;
        margin-bottom: 20px;
        background-color: white;
        transition: transform 0.3s ease;
    }
    
    .news-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    
    /* Investor card styling */
    .investor-card {
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        padding: 15px;
        margin-bottom: 15px;
        background-color: white;
        border-left: 4px solid #2c3e50;
    }
    
    /* Fix select box cursor */
    div[data-baseweb="select"] > div {
        cursor: pointer !important;
    }
</style>
""", unsafe_allow_html=True)

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
    Fetch news from multiple sources with image extraction and classification
    """
    news_sources = [
        {
            'name': 'TechCrunch Startups',
            'url': 'https://techcrunch.com/category/startups/feed/',
            'default_image': 'https://techcrunch.com/wp-content/uploads/2023/01/startup-tech-logo.jpg',
            'category': 'Tech Startups'
        },
        {
            'name': 'TechCrunch AI',
            'url': 'https://techcrunch.com/category/artificial-intelligence/feed/',
            'default_image': 'https://techcrunch.com/wp-content/uploads/2021/07/GettyImages-1207206237.jpg',
            'category': 'AI/ML'
        },
        {
            'name': 'TechCrunch Fintech',
            'url': 'https://techcrunch.com/category/fintech/feed/',
            'default_image': 'https://techcrunch.com/wp-content/uploads/2020/10/GettyImages-1021295824.jpg',
            'category': 'FinTech'
        },
        {
            'name': 'Y Combinator Blog',
            'url': 'https://blog.ycombinator.com/feed/',
            'default_image': 'https://blog.ycombinator.com/wp-content/uploads/2019/03/yc-logo.png',
            'category': 'Startup Advice'
        },
        {
            'name': 'The Ken',
            'url': 'https://the-ken.com/feed/',
            'default_image': 'https://the-ken.com/wp-content/uploads/2020/10/the-ken-logo.png',
            'category': 'Asian Startups'
        }
    ]
    
    all_news = []
    
    for source in news_sources:
        try:
            feed = feedparser.parse(source['url'])
            
            for entry in feed.entries[:5]:  # Get more entries to find ones with images
                # Try to find an image in the entry
                image_url = source['default_image']
                
                # Check for media content in the entry
                if hasattr(entry, 'media_content'):
                    for media in entry.media_content:
                        if media.get('type', '').startswith('image/'):
                            image_url = media['url']
                            break
                
                # Check for enclosures
                elif hasattr(entry, 'enclosures'):
                    for enclosure in entry.enclosures:
                        if enclosure.get('type', '').startswith('image/'):
                            image_url = enclosure['href']
                            break
                
                # Check for image in content
                elif hasattr(entry, 'content'):
                    for content in entry.content:
                        if '<img' in content.value:
                            import re
                            img_match = re.search(r'<img[^>]+src="([^">]+)"', content.value)
                            if img_match:
                                image_url = img_match.group(1)
                                break
                
                # Try to download the image
                image_data = None
                try:
                    response = requests.get(image_url, timeout=5)
                    if response.status_code == 200:
                        if 'image' in response.headers.get('Content-Type', ''):
                            image_data = response.content
                except:
                    pass
                
                news_item = {
                    'title': entry.title,
                    'link': entry.link,
                    'source': source['name'],
                    'published': entry.get('published', 'Recent'),
                    'description': entry.get('summary', 'No description available'),
                    'image_url': image_url,
                    'image_data': image_data,
                    'category': source['category']
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
            response = openai.ChatCompletion.create(
                model="gpt-4.1",
                messages=[
                    {"role": "system", "content": "You are an expert startup investor matcher."},
                    {"role": "user", "content": f"""
                    Analyze this startup idea in the {industry} industry at {funding_stage} stage:
                    
                    {startup_idea}
                    
                    Provide 3-5 most critical factors that would make this startup attractive to investors.
                    """} 
                ]
            )
            
            analysis = response["choices"][0]["message"]["content"]
        except Exception as e:
            st.error(f"OpenAI API Error: {e}")
            analysis = f"This {industry} startup at {funding_stage} stage would likely appeal to investors focused on innovation, market potential, and scalability."
    else:
        analysis = f"For a {industry} startup at {funding_stage} stage, these investors have a proven track record."
    
    return relevant_investors, analysis

def main():
    """
    Main Streamlit application
    """
    # Custom header with logo and tagline
    st.markdown("""
    <div style="background-color:#2c3e50;padding:20px;border-radius:10px;margin-bottom:30px">
        <h1 style="color:white;text-align:center;">🚀 cofounder.ai</h1>
        <p style="color:white;text-align:center;margin-bottom:0;">Your AI-powered startup intelligence platform</p>
    </div>
    """, unsafe_allow_html=True)
    
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
                        model="gpt-4.1",
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
                    
                    # Display feedback in a styled container
                    with st.expander("🔍 AI Analysis Results", expanded=True):
                        st.markdown(f"""
                        <div style="background-color:#f0f2f6;padding:15px;border-radius:10px;">
                            {feedback}
                        </div>
                        """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"AI Analysis Error: {e}")
    
    with tab2:
        st.header("Investor Matching - India's Top Investors")
        
        # Startup Details
        startup_idea = st.text_area("Describe Your Startup Concept", height=150, 
                                   placeholder="Describe your startup idea in 2-3 sentences...")
        
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
        
        # Find Investors Button with better styling
        if st.button("🚀 Find Matching Investors", use_container_width=True):
            with st.spinner("Analyzing your startup and matching with top investors..."):
                matched_investors, analysis = match_investors(startup_idea, industry, funding_stage)
                
                # Display analysis in a styled container
                st.subheader("🔍 Startup Analysis")
                st.markdown(f"""
                <div style="background-color:#e8f4fd;padding:15px;border-radius:10px;border-left:4px solid #2c3e50;">
                    {analysis}
                </div>
                """, unsafe_allow_html=True)
                
                # Display matched investors
                st.subheader("🌟 Top Recommended Investors")
                
                # Display investors in cards
                for i, investor in enumerate(matched_investors):
                    st.markdown(f"""
                    <div class="investor-card">
                        <h3>{i+1}. {investor['name']}</h3>
                        <p><strong>Focus:</strong> {investor['focus']}</p>
                        <p><strong>Location:</strong> {investor['location']}</p>
                        <p><strong>Typical Investment:</strong> {investor['typical_check']}</p>
                        <p><strong>Notable Investments:</strong> {investor['portfolio']}</p>
                        <p><a href="{investor['website']}" target="_blank">Visit Website</a></p>
                    </div>
                    """, unsafe_allow_html=True)
    
    with tab3:
        st.header("📰 Latest Startup News")
        
        # Refresh button with better styling
        if st.button("🔄 Refresh News", key="refresh_news"):
            st.rerun()
        
        # Add news category filter
        news_items = fetch_enhanced_news()
        
        if news_items:
            # Get unique categories
            categories = list(set([item['category'] for item in news_items]))
            categories.insert(0, "All Categories")
            
            selected_category = st.selectbox("Filter by Category", categories)
            
            # Filter news by category
            if selected_category != "All Categories":
                news_items = [item for item in news_items if item['category'] == selected_category]
            
            # Create 3-column layout
            cols = st.columns(3)
            
            # Display news items in cards
            for i, news in enumerate(news_items):
                col = cols[i % 3]  # Distribute across columns
                
                with col:
                    # Create a news card
                    st.markdown(f"""
                    <div class="news-card">
                        <h4>{news['title']}</h4>
                        <p><small><strong>{news['source']}</strong> | {news['category']}</small></p>
                        <p><small>{news['published']}</small></p>
                    """, unsafe_allow_html=True)
                    
                    # Display image if available
                    if news['image_data']:
                        try:
                            image = Image.open(io.BytesIO(news['image_data']))
                            st.image(image, use_container_width=True)
                        except Exception as e:
                            st.warning("Could not display image")
                    
                    # Continue the card HTML
                    st.markdown(f"""
                        <p>{news['description'][:150]}...</p>
                        <a href="{news['link']}" target="_blank">Read more</a>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("No news available at the moment. Please try again later.")

if __name__ == "__main__":
    main()
