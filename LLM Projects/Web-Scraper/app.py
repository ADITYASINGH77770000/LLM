import streamlit as st 
import google.generativeai as genai
from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup

# Load API key
load_dotenv()
google_api_key = os.getenv("GEMINI_API_KEY")

if not google_api_key:
    st.error("Gemini API key not set in .env file")
else:
    genai.configure(api_key=google_api_key)
    
# Function to scrape website 
def scrape_website(url):
    headers = {"User-Agent": "Mozilla/5.0 "}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        text = ' '.join([p.get_text() for p in paragraphs])
        return text[:3000]
    else:
        return f"Failed to retrive content, status code: {response.status_code}"
    
# Streamlit ui
st.title("Web Scraper 🤖")

url = st.text_input("Enter Website URL")

if st.button("Analyze"):
    with st.spinner("Scraping website..."):
        scraped_text = scrape_website(url)

    if "Failed" not in scraped_text:
        with st.spinner("Generating insights using Gemini AI..."):
            system_message = "You are an AI analyst that extracts key insights from web content."
            user_message = f"""
            Analyze the following content and provide a detailed report with:
            1. **Main Features** - What are the core topics covered?
            2. **Tools & Technologies** - What tools, libraries, or frameworks are mentioned?
            3. **Future Trends & Goals** - What upcoming innovations or directions does the content suggest?
            4. **Summary for Time-Sensitive Users** - A quick 2-3 sentence version for users in a hurry.

            Content to analyze:
            {scraped_text}
            """

            gemini = genai.GenerativeModel("gemini-1.5-flash")
            stream = gemini.generate_content(user_message, stream=True)

            reply = ""
            for chunk in stream:
                content = chunk.text or ""
                reply += content

            # Display output
            st.markdown(reply)
    else:
        st.error(scraped_text)