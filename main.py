import streamlit as st
from groq import Groq
import re

# Access the API key from Streamlit secrets
llama_api_key = st.secrets["api_keys"]["LLAMA_API_KEY"]

# Initialize the Groq client
client = Groq(api_key=llama_api_key)

def generate_tamil_poetry(style, theme, max_tokens=800):
    system_prompt = """You are a master Tamil poet with deep knowledge of Tamil literature, linguistics, and culture. 
    Generate authentic, high-quality Tamil poetry that strictly adheres to the requested style and theme. 
    Ensure all Tamil words are spelled correctly and the English translation accurately reflects the Tamil content."""

    style_prompts = {
        "haiku": f"""Create a Tamil haiku on '{theme}':
        1. Three lines capturing a single moment or image.
        2. Concise and evocative language.
        3. Aim for about 10-14 syllables total.
        4. Focused on the theme: {theme}.
        5. Use culturally relevant imagery and metaphors.""",
        
        "venba": f"""Compose a Tamil venba on '{theme}':
        1. Four lines: two கூற்று (kūṟṟu), one தாழிசை (tāḻicai), ending with சுருங்கடி (curuṅkaṭi).
        2. Follow venba meter: நேர் (nēr) and நிரை (nirai) patterns strictly.
        3. Ensure the last foot of each line is இயற்சீர் (iyaṟcīr).
        4. The final word must be a single syllable.
        5. Theme: {theme}.
        6. Incorporate classical Tamil concepts and imagery.""",
        
        "free verse": f"""Write a Tamil free verse poem on '{theme}':
        1. Use vivid Tamil imagery and metaphors.
        2. Incorporate classical Tamil literary devices like உவமை (uvmai) or உருவகம் (uruvakam).
        3. Experiment with line breaks for emotional impact.
        4. Blend traditional and modern elements.
        5. Focus on the theme: {theme}.
        6. Ensure the poem has depth and cultural relevance."""
    }

    user_prompt = style_prompts.get(style.lower(), style_prompts["free verse"])
    user_prompt += """ 
    Provide the poem in this format:

    தமிழ் (Tamil):
    [Poem in Tamil script]

    ஒலிப்பெயர்ப்பு (Transliteration):
    [Accurate Romanized transliteration]

    English Translation:
    [Precise and poetic translation]

    Explanation:
    [Detailed explanation of poetic elements, cultural references, and how it relates to the theme]
    """

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

def format_poem(poem_text):
    sections = re.split(r'\n\s*\n', poem_text)
    formatted_sections = []
    for section in sections:
        if ":" in section:
            title, content = section.split(":", 1)
            formatted_sections.append(f"**{title.strip()}:**\n{content.strip()}")
        else:
            formatted_sections.append(section.strip())
    return "\n\n".join(formatted_sections)

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
            formatted_poem = format_poem(poem)
            st.markdown(formatted_poem)
    else:
        st.warning("Please enter a theme for your poem.")

st.sidebar.markdown("### About")
st.sidebar.info("This app generates authentic Tamil poetry using AI. It's an educational tool to explore Tamil poetic forms and cultural themes. Created with love by Vidhiya S B (www.x.com/Vidhiyasb)")
