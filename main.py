import streamlit as st
from groq import Groq
import os

# Directly provide the API key (for demonstration purposes, but it's not recommended for production)
API_KEY = "your_api_key"

# Initialize the Groq client
client = Groq(api_key=API_KEY)

def generate_tamil_poetry(style, theme, max_tokens=500):
    system_prompt = """You are a master Tamil poet with deep knowledge of Tamil literature and linguistics. 
    Generate authentic, high-quality Tamil poetry that strictly adheres to the requested style and theme."""

    style_prompts = {
        "haiku": f"""Create a Tamil haiku on '{theme}':
        1. Three lines capturing a single moment or image.
        2. Concise and evocative language.
        3. Aim for about 10-14 syllables total.
        4. Focused on the theme: {theme}.""",
        "venba": f"""Compose a Tamil venba on '{theme}':
        1. Four lines: two கூற்று (kūṟṟu), one or two தாழிசை (tāḻicai), ending with குறள் (kural) or சிந்து (cintu).
        2. Follow venba meter: நேர் (nēr) and நிரை (nirai) patterns.
        3. Ensure the last foot of each line is இயற்சீர் (iyaṟcīr).
        4. The final word must be a single syllable.
        5. Theme: {theme}.""",
        "free verse": f"""Write a Tamil free verse poem on '{theme}':
        1. Use vivid Tamil imagery and metaphors.
        2. Incorporate classical Tamil literary devices like உவமை (uvmai) or உருவகம் (uruvakam).
        3. Experiment with line breaks for emotional impact.
        4. Blend traditional and modern elements.
        5. Focus on the theme: {theme}."""
    }

    user_prompt = style_prompts.get(style.lower(), style_prompts["free verse"])
    user_prompt += """
Provide the poem in this format:
தமிழ் (Tamil):
[Poem in Tamil script]

ஒலிப்பெயர்ப்பு (Transliteration):
[Romanized transliteration]

English Translation:
[Your translation]

Explanation:
[Brief explanation of poetic elements and how it relates to the theme]"""

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.7
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None

st.title("Tamil Poetry Generator")

style = st.selectbox("Choose a poetry style:", ["Haiku", "Venba", "Free Verse"])
theme = st.text_input("Enter a theme for your poem:")

if st.button("Generate Poem"):
    if theme:
        with st.spinner("கவிதை உருவாக்கப்படுகிறது... (Generating poem...)"):
            poem = generate_tamil_poetry(style, theme)
        if poem:
            st.success("கவிதை வெற்றிகரமாக உருவாக்கப்பட்டது! (Poem generated successfully!)")
            st.markdown("### Your Tamil Poem:")
            st.write(poem)
    else:
        st.warning("Please enter a theme for your poem.")

st.sidebar.markdown("### About")
st.sidebar.info("This app generates Tamil poetry using AI. It's an educational tool to explore Tamil poetic forms. Created with love by Vidhiya S B (www.x.com/Vidhiyasb)")
