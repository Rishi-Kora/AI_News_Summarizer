import streamlit as st
import os
from dotenv import load_dotenv
from tenacity import RetryError
from utils import extract_text_from_url, generate_summary, rewrite_text

# Load environment variables
load_dotenv()

# Page Config
st.set_page_config(page_title="AI News Summarizer",layout="wide")

# Custom CSS for styling
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6;
    }
    .main-header {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        color: #333;
        text-align: left;
        padding-bottom: 20px;
    }
    .stButton>button {
        width: 100%;
        background-color: #ff4b4b;
        color: white;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# API Key Handling
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ GEMINI_API_KEY not found in environment variables (.env). Please set it to use the app.")
    st.stop()

# Main Content
st.markdown("<h1 class='main-header'>AI News Summarizer</h1>", unsafe_allow_html=True)

url_input = st.text_input("Enter Article URL", placeholder="https://example.com/news-article")

if url_input:
    if not api_key:
        st.error("API Key is missing!")
    else:
        text_content = ""
        with st.spinner("Fetching content..."):
            text_content = extract_text_from_url(url_input)
            
        if "Error" in text_content:
            st.error(text_content)
        else:
            # We have text, now process
            with st.spinner("Analyzing..."):
                try:
                    # Summary
                    summary = generate_summary(text_content, api_key)
                    
                    st.markdown("### Summary")
                    st.markdown(summary)

                except RetryError:
                    st.error("⚠️ API Rate Limit Exceeded. The system is currently busy. Please try again later.")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")
