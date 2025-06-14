import streamlit as st
import fitz  # PyMuPDF
import pytesseract
from pptx import Presentation
from PIL import Image
import openai
import requests
import feedparser
import pandas as pd
import io
import time
from datetime import datetime
import json
import stripe

# Configure Stripe for payments (you'll need to set up your Stripe account)
stripe.api_key = st.secrets["STRIPE_API_KEY"]

# Premium features configuration
PREMIUM_FEATURES = {
    "investor_contact_info": True,
    "detailed_funding_reports": True,
    "competitor_analysis": True,
    "market_size_estimates": True,
    "export_reports": True
}

# Configure Streamlit page with premium look
st.set_page_config(
    page_title="cofounder.ai | Startup Intelligence Platform",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium CSS styling
st.markdown("""
<style>
    /* Main app styling */
    .stApp {
        background-color: #f9fafc;
    }
    
    /* Premium header */
    .premium-header {
        background: linear-gradient(135deg, #6e48aa 0%, #9d50bb 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    /* Premium cards */
    .premium-card {
        border-radius: 12px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.08);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        background: white;
        border-left: 5px solid #6e48aa;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .premium-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.12);
    }
    
    /* Premium button */
    .stButton>button {
        background: linear-gradient(135deg, #6e48aa 0%, #9d50bb 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(110,72,170,0.3);
        color: white;
    }
    
    /* Premium tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: #f3f4f6;
        border-radius: 8px 8px 0 0;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s ease;
        font-weight: 500;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: #e5e7eb;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6e48aa 0%, #9d50bb 100%);
        color: white;
    }
    
    /* Lock icon for premium features */
    .premium-lock {
        color: #9d50bb;
        font-size: 1rem;
        margin-left: 0.5rem;
    }
    
    /* Subscription plans */
    .pricing-card {
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        background: white;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        border: 1px solid #e5e7eb;
    }
    
    .pricing-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        border-color: #9d50bb;
    }
    
    .pricing-card.featured {
        border: 2px solid #6e48aa;
        position: relative;
    }
    
    .featured-badge {
        position: absolute;
        top: -12px;
        right: 20px;
        background: #6e48aa;
        color: white;
        padding: 0.25rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'premium_user' not in st.session_state:
    st.session_state.premium_user = False

# Configure OpenAI API
openai.api_key = st.secrets["OPENAI_API_KEY"]

# ========== MONETIZATION FUNCTIONS ==========
def show_pricing_plans():
    """Display pricing plans for premium features"""
    st.header("🚀 Upgrade to Premium")
    st.markdown("Unlock powerful startup intelligence tools to accelerate your fundraising and growth")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="pricing-card">
            <h3>Founder</h3>
            <h2>$29/month</h2>
            <p>Perfect for early-stage founders</p>
            <hr>
            <p>✓ Basic investor matching</p>
            <p>✓ 10 AI analyses/month</p>
            <p>✓ Standard reports</p>
            <p>✗ No competitor analysis</p>
            <p>✗ No investor contacts</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Choose Founder Plan", key="founder_plan"):
            handle_subscription("price_1P9Z3jSB2J9X9X9X9X9X9X9X")  # Example Stripe price ID
    
    with col2:
        st.markdown("""
        <div class="pricing-card featured">
            <div class="featured-badge">POPULAR</div>
            <h3>Startup Pro</h3>
            <h2>$99/month</h2>
            <p>For serious fundraising</p>
            <hr>
            <p>✓ Advanced investor matching</p>
            <p>✓ 50 AI analyses/month</p>
            <p>✓ Detailed reports</p>
            <p>✓ Competitor analysis</p>
            <p>✓ Investor email contacts</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Choose Startup Pro Plan", key="pro_plan", type="primary"):
            handle_subscription("price_1P9Z3jSB2J9X9X9X9X9X9X9X")  # Example Stripe price ID
    
    with col3:
        st.markdown("""
        <div class="pricing-card">
            <h3>Enterprise</h3>
            <h2>$299/month</h2>
            <p>For VCs and accelerators</p>
            <hr>
            <p>✓ Unlimited investor matching</p>
            <p>✓ Unlimited AI analyses</p>
            <p>✓ Premium reports</p>
            <p>✓ Full competitor analysis</p>
            <p>✓ Investor direct contacts</p>
            <p>✓ API Access</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Choose Enterprise Plan", key="enterprise_plan"):
            handle_subscription("price_1P9Z3jSB2J9X9X9X9X9X9X9X")  # Example Stripe price ID

def handle_subscription(price_id):
    """Handle Stripe subscription"""
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': price_id,
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=st.secrets["STRIPE_SUCCESS_URL"],
            cancel_url=st.secrets["STRIPE_CANCEL_URL"],
        )
        st.session_state.stripe_session_id = checkout_session.id
        st.write(f"Please complete your payment [here]({checkout_session.url})")
    except Exception as e:
        st.error(f"Error creating checkout session: {e}")

def check_premium_access():
    """Check if user has premium access"""
    # In a real app, you would check against your user database
    return st.session_state.premium_user

def show_premium_lock(feature_name):
    """Show premium lock for features"""
    st.warning(f"🔒 {feature_name} is a premium feature. Upgrade to access this functionality.")
    if st.button("Upgrade Now"):
        show_pricing_plans()

# ========== CORE BUSINESS FUNCTIONS ==========
def generate_competitor_analysis(startup_idea, industry):
    """Generate detailed competitor analysis using AI"""
    if not check_premium_access():
        show_premium_lock("Competitor Analysis")
        return None
    
    with st.spinner("Analyzing competitors..."):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a startup competitive intelligence analyst."},
                    {"role": "user", "content": f"""
                    Analyze the competitive landscape for this startup idea in the {industry} industry:
                    
                    {startup_idea}
                    
                    Provide:
                    1. Direct competitors with their funding status
                    2. Market positioning analysis
                    3. Competitive advantages
                    4. Potential threats
                    5. Market share estimates
                    """}
                ]
            )
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            st.error(f"Error generating analysis: {e}")
            return None

def generate_funding_strategy(startup_idea, industry, stage):
    """Generate personalized funding strategy"""
    with st.spinner("Creating funding strategy..."):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4.1",
                messages=[
                    {"role": "system", "content": "You are a startup funding strategist."},
                    {"role": "user", "content": f"""
                    Create a detailed funding strategy for this {industry} startup at {stage} stage:
                    
                    {startup_idea}
                    
                    Include:
                    1. Recommended funding sources
                    2. Ideal investor profile
                    3. Valuation benchmarks
                    4. Funding timeline
                    5. Key metrics to focus on
                    """}
                ]
            )
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            st.error(f"Error generating strategy: {e}")
            return None

def generate_pitch_deck_review(deck_text):
    """Generate detailed pitch deck review"""
    if not check_premium_access():
        show_premium_lock("Pitch Deck Review")
        return None
    
    with st.spinner("Analyzing pitch deck..."):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4.1",
                messages=[
                    {"role": "system", "content": "You are a pitch deck expert who has reviewed thousands of decks."},
                    {"role": "user", "content": f"""
                    Provide a detailed review of this pitch deck:
                    
                    {deck_text}
                    
                    Cover:
                    1. Strengths and weaknesses
                    2. Storytelling effectiveness
                    3. Financial projections quality
                    4. Design recommendations
                    5. Suggested improvements
                    """}
                ]
            )
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            st.error(f"Error analyzing deck: {e}")
            return None

# ========== MAIN APP ==========
def main():
    """Main application interface"""
    
    # Premium header
    st.markdown("""
    <div class="premium-header">
        <h1 style="color:white;margin:0;">cofounder.ai</h1>
        <p style="color:white;margin:0;font-size:1.2rem;">The AI-powered startup intelligence platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Authentication check
    if not st.session_state.authenticated:
        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Login"):
                # In a real app, verify credentials against your database
                st.session_state.authenticated = True
                st.session_state.premium_user = True  # For demo purposes
                st.rerun()
        with col2:
            if st.button("Sign Up"):
                show_pricing_plans()
        return
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🏠 Dashboard", "💰 Fundraising", "📊 Analytics", "⚙️ Account"])
    
    with tab1:
        st.header("Startup Intelligence Dashboard")
        
        # Quick analysis section
        with st.expander("🚀 Quick Startup Analysis", expanded=True):
            startup_idea = st.text_area("Describe your startup (2-3 sentences)", height=100)
            industry = st.selectbox("Industry", ["Tech", "FinTech", "HealthTech", "EdTech", "AI/ML", "E-commerce", "Other"])
            
            if st.button("Analyze My Startup"):
                if startup_idea.strip():
                    with st.spinner("Generating insights..."):
                        # Generate multiple analyses in parallel
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("""
                            <div class="premium-card">
                                <h4>Competitive Landscape</h4>
                            """, unsafe_allow_html=True)
                            analysis = generate_competitor_analysis(startup_idea, industry)
                            if analysis:
                                st.write(analysis)
                            st.markdown("</div>", unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown("""
                            <div class="premium-card">
                                <h4>Funding Strategy</h4>
                            """, unsafe_allow_html=True)
                            strategy = generate_funding_strategy(startup_idea, industry, "Seed")
                            if strategy:
                                st.write(strategy)
                            st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.warning("Please describe your startup idea")
        
        # Recent activity section
        st.markdown("""
        <div class="premium-card">
            <h4>📈 Your Startup Health Score</h4>
            <p>Coming soon: Track your startup's progress across key metrics</p>
        </div>
        """, unsafe_allow_html=True)
    
    with tab2:
        st.header("Fundraising Toolkit")
        
        # Investor matching section
        with st.expander("🔍 Smart Investor Matching", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                funding_stage = st.selectbox("Funding Stage", ["Pre-Seed", "Seed", "Series A", "Series B", "Growth"])
                industry = st.selectbox("Industry", ["Tech", "FinTech", "HealthTech", "EdTech", "AI/ML", "E-commerce"])
            with col2:
                geography = st.selectbox("Geography", ["Global", "North America", "Europe", "Asia", "India"])
                ticket_size = st.selectbox("Ticket Size", ["$100K-$500K", "$500K-$2M", "$2M-$5M", "$5M-$10M", "$10M+"])
            
            if st.button("Find Investors"):
                # Simulate investor matching
                with st.spinner("Matching with ideal investors..."):
                    time.sleep(2)
                    
                    # Display premium investor cards
                    st.markdown("""
                    <div class="premium-card">
                        <h4>Sequoia Capital</h4>
                        <p><strong>Focus:</strong> Early-stage tech, AI/ML, SaaS</p>
                        <p><strong>Recent Investments:</strong> 15 in last 6 months</p>
                        <p><strong>Match Score:</strong> 92%</p>
                        <button>View Full Profile (Premium)</button>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("""
                    <div class="premium-card">
                        <h4>Accel Partners</h4>
                        <p><strong>Focus:</strong> FinTech, Marketplaces</p>
                        <p><strong>Recent Investments:</strong> 8 in last 6 months</p>
                        <p><strong>Match Score:</strong> 87%</p>
                        <button>View Full Profile (Premium)</button>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Pitch deck analyzer
        with st.expander("📑 AI Pitch Deck Review", expanded=True):
            uploaded_file = st.file_uploader("Upload your pitch deck (PDF or PPTX)", type=["pdf", "pptx"])
            if uploaded_file:
                with st.spinner("Extracting content..."):
                    # Extract text from file
                    text = ""
                    if uploaded_file.type == "application/pdf":
                        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                        text = "\n".join([page.get_text("text") for page in doc])
                    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.presentationml.presentation":
                        prs = Presentation(uploaded_file)
                        text = "\n".join(["\n".join([shape.text for shape in slide.shapes if hasattr(shape, "text")]) for slide in prs.slides])
                
                if text:
                    review = generate_pitch_deck_review(text)
                    if review:
                        st.markdown(f"""
                        <div class="premium-card">
                            <h4>Pitch Deck Analysis</h4>
                            {review}
                        </div>
                        """, unsafe_allow_html=True)
    
    with tab3:
        st.header("Advanced Analytics")
        
        if not check_premium_access():
            show_pricing_plans()
            return
        
        # Market analysis section
        with st.expander("🌍 Market Size Analysis", expanded=True):
            industry = st.selectbox("Select Industry", ["FinTech", "EdTech", "HealthTech", "AI/ML", "E-commerce"])
            region = st.selectbox("Select Region", ["Global", "North America", "Europe", "Asia", "India"])
            
            if st.button("Generate Market Report"):
                with st.spinner("Generating market intelligence..."):
                    time.sleep(3)
                    
                    # Simulate market analysis report
                    st.markdown("""
                    <div class="premium-card">
                        <h4>Market Analysis: {industry} in {region}</h4>
                        <p><strong>Total Addressable Market:</strong> $12.4B (2024)</p>
                        <p><strong>Growth Rate:</strong> 18.7% CAGR</p>
                        <p><strong>Key Segments:</strong></p>
                        <ul>
                            <li>Segment A: $4.2B (34%)</li>
                            <li>Segment B: $3.1B (25%)</li>
                            <li>Segment C: $2.8B (23%)</li>
                        </ul>
                        <p><strong>Top Players:</strong> Company X (22% share), Company Y (18%), Company Z (12%)</p>
                        <button>Download Full Report (PDF)</button>
                    </div>
                    """.format(industry=industry, region=region), unsafe_allow_html=True)
        
        # Competitive intelligence
        with st.expander("🕵️ Competitor Intelligence", expanded=True):
            company_name = st.text_input("Enter competitor name")
            if company_name and st.button("Analyze Competitor"):
                with st.spinner("Gathering competitive intelligence..."):
                    time.sleep(3)
                    
                    # Simulate competitor analysis
                    st.markdown("""
                    <div class="premium-card">
                        <h4>Competitor Analysis: {company_name}</h4>
                        <p><strong>Funding:</strong> Series B ($15M raised)</p>
                        <p><strong>Growth Rate:</strong> 120% YoY</p>
                        <p><strong>Key Metrics:</strong></p>
                        <ul>
                            <li>ARR: $8.2M</li>
                            <li>Customers: 1,250</li>
                            <li>Team Size: 85</li>
                        </ul>
                        <p><strong>Strengths:</strong> Strong brand, efficient CAC</p>
                        <p><strong>Weaknesses:</strong> High churn, concentrated customer base</p>
                        <button>View Full Analysis</button>
                    </div>
                    """.format(company_name=company_name), unsafe_allow_html=True)
    
    with tab4:
        st.header("Account Settings")
        
        if check_premium_access():
            st.success("🌟 You are on a Premium Plan (Startup Pro)")
            st.write("Next billing date: March 15, 2024")
            
            if st.button("Manage Subscription"):
                # In a real app, link to Stripe customer portal
                st.write("Redirecting to subscription management...")
            
            if st.button("Download Invoice"):
                st.write("Invoice downloaded")
        else:
            show_pricing_plans()

if __name__ == "__main__":
    main()
