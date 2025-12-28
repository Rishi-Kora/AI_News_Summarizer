import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import os

def extract_text_from_url(url):
    """
    Fetches the content of a URL and extracts the text.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
            
        text = soup.get_text(separator=' ')
        
        # Basic cleanup
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text[:5000] # Truncate to avoid huge prompts and save tokens
    except Exception as e:
        return f"Error extracting text: {e}"

from tenacity import retry, stop_after_attempt, wait_random_exponential, retry_if_exception_type
from google.api_core.exceptions import ResourceExhausted

@retry(
    stop=stop_after_attempt(3),
    wait=wait_random_exponential(multiplier=2, max=60),
    retry=retry_if_exception_type(ResourceExhausted)
)
def generate_summary(text, api_key):
    """
    Generates a 3-bullet point summary using Gemini, trying multiple models.
    """
    genai.configure(api_key=api_key)
    
    models_to_try = [
        'gemini-2.0-flash-lite',
        'gemini-2.0-flash', 
        'gemini-2.5-flash',
        'gemini-flash-lite-latest',
        'gemini-2.0-flash-exp'
    ]
    
    last_exception = None
    
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            
            prompt = f"""
            You are a helpful news assistant. 
            Please summarize the following text into exactly three concise bullet points.
            
            Text:
            {text}
            """
            
            response = model.generate_content(prompt)
            return response.text
        except ResourceExhausted as e:
            last_exception = e
            continue # Try next model
        except Exception as e:
            # If 429 in message, treat as ResourceExhausted
            if "429" in str(e):
                last_exception = e
                continue
            return f"Error generating summary with {model_name}: {e}"
            
    # If all models failed with ResourceExhausted, raise it so Tenacity can retry the whole batch
    if last_exception:
        raise last_exception
    return "Error: Could not generate summary."

@retry(
    stop=stop_after_attempt(5),
    wait=wait_random_exponential(multiplier=1, max=60),
    retry=retry_if_exception_type(ResourceExhausted)
)
def rewrite_text(text, style, api_key):
    """
    Rewrites the text in a specific style using Gemini.
    """
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        style_prompts = {
            "ELI5": "Explain this like I'm 5 years old.",
            "Shakespeare": "Rewrite this as a Shakespearean sonnet.",
            "Professional": "Rewrite this in a strictly professional and executive tone.",
            "Tweet": "Rewrite this as a viral tweet thread (max 280 chars per tweet, max 3 tweets).",
            "Pirate": "Rewrite this in the voice of a pirate captain."
        }
        
        specific_instruction = style_prompts.get(style, "Rewrite this text.")
        
        prompt = f"""
        {specific_instruction}
        
        Text to rewrite:
        {text}
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error rewriting text: {e}"
