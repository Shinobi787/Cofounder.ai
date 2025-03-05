import streamlit as st
import fitz  # PyMuPDF for PDFs
import pytesseract  # OCR for images
from pptx import Presentation
from PIL import Image
import openai
import requests

# Set OpenAI API Key
OPENAI_API_KEY = "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"
openai.api_key = OPENAI_API_KEY

# Function to Fetch Startup Funding News
def fetch_startup_news():
    url = "https://techcrunch.com/startups/"
    response = requests.get(url)
    if response.status_code == 200:
        return "Latest startup funding news fetched successfully! (TechCrunch integration placeholder)"
    else:
        return "Failed to fetch latest funding news. Try again later."

# Streamlit UI Configuration
st.set_page_config(page_title="AI Slide & Investor Analyzer", layout="wide")
st.title("📊 AI Slide & Investor Analyzer")

# Navigation Tabs
tab1, tab2, tab3 = st.tabs(["📑 Slide Analyzer", "💰 Investor Matching", "📰 Startup Funding News"])

# ---- Slide Analyzer Section ----
with tab1:
    st.header("📑 AI Slide Analyzer")
    st.write("Upload your presentation (PPTX, PDF, or Image) to receive AI-powered feedback.")
    
    # User Inputs
    user_category = st.selectbox("Who are you?", ["Student", "Educator", "Business Professional", "Startup Founder", "Other"])
    purpose = st.selectbox("What is the purpose of your presentation?", ["Business", "Academic", "Pitch", "Report", "Other"])
    desired_action = st.selectbox("What do you want to do with this content?", ["Summarize", "Extract Key Points", "Get AI Suggestions"])
    detail_level = st.slider("How detailed should the AI analysis be? (1 - Basic, 10 - In-depth)", 1, 10, 5)
    
    # File Upload
    uploaded_file = st.file_uploader("Upload PPTX, PDF, or Image", type=["pptx", "pdf", "png", "jpg", "jpeg"])
    
    def extract_text(file):
        if file.type == "application/pdf":
            doc = fitz.open(stream=file.read(), filetype="pdf")
            return "\n".join([page.get_text("text") for page in doc])
        elif file.type == "application/vnd.openxmlformats-officedocument.presentationml.presentation":
            prs = Presentation(file)
            return "\n".join(["\n".join([shape.text for shape in slide.shapes if hasattr(shape, "text")]) for slide in prs.slides])
        else:
            image = Image.open(file)
            return pytesseract.image_to_string(image)
    
    if uploaded_file:
        with st.spinner("Extracting text & analyzing..."):
            extracted_text = extract_text(uploaded_file)
            prompt = f"""
            Analyze this presentation content for {purpose}, user type {user_category}, with detail level {detail_level}.
            Provide feedback on clarity, engagement, structure, effectiveness, and suggest improvements.
            Text:
            {extracted_text}
            """
            response = openai.ChatCompletion.create(
                model="gpt-4-turbo",
                messages=[{"role": "system", "content": prompt}]
            )
            feedback = response["choices"][0]["message"]["content"]
        
        # Display Feedback
        st.subheader("📌 AI Feedback")
        st.write(feedback)
        
        # Post-Analysis Rating
        st.subheader("⭐ Rate Your Experience")
        rating = st.slider("How accurate was the analysis?", 1, 5, 3)
        user_feedback = st.text_area("Any suggestions?")
        if st.button("Submit Feedback"):
            st.success("Thank you for your feedback!")

# ---- Investor Matching Section ----
with tab2:
    st.header("💰 AI Investor Matching")
    st.write("Find the best investors based on your idea and funding needs.")
    
    startup_idea = st.text_area("Describe your startup idea")
    funding_stage = st.selectbox("What is your funding stage?", ["Pre-Seed", "Seed", "Series A", "Series B", "Growth Stage"])
    industry = st.selectbox("Which industry are you in?", ["Tech", "Healthcare", "Finance", "E-commerce", "Other"])
    
    if st.button("Find Investors"):
        with st.spinner("Analyzing market & finding best investors..."):
            investor_prompt = f"""
            Identify potential investors who fund {industry} startups at {funding_stage} stage.
            Analyze news trends, past investment history, and provide a ranked list of best-fit investors.
            """
            investor_response = openai.ChatCompletion.create(
                model="gpt-4-turbo",
                messages=[{"role": "system", "content": investor_prompt}]
            )
            investors = investor_response["choices"][0]["message"]["content"]
        
        st.subheader("🔍 Recommended Investors")
        st.write(investors)

# ---- Startup Funding News ----
with tab3:
    st.header("📰 Latest Startup Funding News")
    st.write("Stay updated with the latest funding rounds and investments.")
    
    if st.button("Fetch Latest News"):
        with st.spinner("Fetching latest startup funding news..."):
            news_data = fetch_startup_news()
        st.write(news_data)

# Responsive Design Adjustments
st.markdown("""
    <style>
    @media (min-width: 768px) {
        body { font-size: 20px; }
    }
    @media (max-width: 767px) {
        body { font-size: 16px; }
    }
    </style>
""", unsafe_allow_html=True)
