import streamlit as st
from groq import Groq
import re

# Access the API key from Streamlit secrets
llama_api_key = st.secrets["api_keys"]["LLAMA_API_KEY"]

# Initialize the Groq client
client = Groq(api_key=llama_api_key)

def generate_tamil_poetry(style, theme, max_tokens=1000):
    system_prompt = """You are a master Tamil poet with deep knowledge of Tamil literature, linguistics, and culture. 
    Generate authentic, high-quality Tamil poetry that strictly adheres to the requested style and theme. 
    Ensure all Tamil words are spelled correctly, use proper punctuation, and create meaningful content that resonates with Tamil culture and traditions.
    The English translation must accurately reflect the Tamil content, including its nuances and cultural references."""

    style_prompts = {
        "haiku": f"""Create a Tamil haiku on '{theme}':
        1. Three lines capturing a single moment or image.
        2. Concise and evocative language with perfect spelling and punctuation.
        3. Aim for about 10-14 syllables total.
        4. Focus deeply on the theme: {theme}.
        5. Use culturally relevant imagery and metaphors that resonate with Tamil heritage.
        6. Ensure each word contributes to a meaningful and impactful message.""",
        
        "venba": f"""Compose a Tamil venba on '{theme}':
        1. Four lines: two கூற்று (kūṟṟu), one தாழிசை (tāḻicai), ending with சுருங்கடி (curuṅkaṭi).
        2. Follow venba meter: நேர் (nēr) and நிரை (nirai) patterns with utmost precision.
        3. Ensure the last foot of each line is இயற்சீர் (iyaṟcīr).
        4. The final word must be a single syllable.
        5. Theme: {theme} - explore it with depth and insight.
        6. Incorporate classical Tamil concepts, proverbs, or references to literature.
        7. Use flawless spelling and appropriate punctuation to enhance readability.""",
        
        "free verse": f"""Write a Tamil free verse poem on '{theme}':
        1. Use vivid Tamil imagery and metaphors that are deeply rooted in Tamil culture.
        2. Incorporate classical Tamil literary devices like உவமை (uvmai) or உருவகம் (uruvakam) with precision.
        3. Experiment with line breaks and punctuation for maximum emotional and aesthetic impact.
        4. Blend traditional and modern elements to create a timeless piece.
        5. Focus intently on the theme: {theme}, offering new perspectives or insights.
        6. Ensure the poem has philosophical depth and strong cultural relevance.
        7. Pay meticulous attention to spelling, word choice, and punctuation."""
    }

    user_prompt = style_prompts.get(style.lower(), style_prompts["free verse"])
    user_prompt += """ 
    Provide the poem in this format:

    தமிழ் (Tamil):
    [Poem in Tamil script with perfect spelling and punctuation]

    ஒலிப்பெயர்ப்பு (Transliteration):
    [Accurate Romanized transliteration with appropriate diacritical marks]

    English Translation:
    [Precise and poetic translation that captures the essence and cultural nuances]

    Explanation:
    [Detailed explanation of poetic elements, cultural references, and how it profoundly relates to the theme. Include any wordplay, double meanings, or subtle cultural allusions.]
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
            formatted_sections.append(f"### {title.strip()}:\n{content.strip()}")
        else:
            formatted_sections.append(section.strip())
    return "\n\n".join(formatted_sections)

def quality_check(poem):
    # This function would implement additional quality checks
    # For now, it's a placeholder for future enhancements
    return poem

st.title("Tamil Poetry Generator")

style = st.selectbox("Choose a poetry style:", ["Haiku", "Venba", "Free Verse"])
theme = st.text_input("Enter a theme for your poem:")

if st.button("Generate Poem"):
    if theme:
        with st.spinner("கவிதை உருவாக்கப்படுகிறது... (Generating poem...)"):
            poem = generate_tamil_poetry(style, theme)
            poem = quality_check(poem)  # Placeholder for additional quality control
        if poem:
            st.success("கவிதை வெற்றிகரமாக உருவாக்கப்பட்டது! (Poem generated successfully!)")
            st.markdown("## Your Tamil Poem:")
            formatted_poem = format_poem(poem)
            st.markdown(formatted_poem)
    else:
        st.warning("Please enter a theme for your poem.")

st.sidebar.markdown("### About")
st.sidebar.info("This app generates authentic Tamil poetry using AI. It creates meaningful, culturally rich poems with correct spelling and punctuation. It's an educational tool to explore Tamil poetic forms and cultural themes. Created with love by Vidhiya S B (www.x.com/Vidhiyasb)")
