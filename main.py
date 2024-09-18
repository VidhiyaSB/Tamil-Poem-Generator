import streamlit as st
from groq import Groq
import re
import random

# Access the API key from Streamlit secrets
llama_api_key = st.secrets["api_keys"]["LLAMA_API_KEY"]

# Initialize the Groq client
client = Groq(api_key=llama_api_key)

# Tamil literature resources
tamil_proverbs = [
    "அகத்தின் அழகு முகத்தில் தெரியும்",
    "யானை இருந்தாலும் குதிரை இருந்தாலும் ஓட்டுநர் திறமையே முக்கியம்",
    "கற்றது கைமண் அளவு, கல்லாதது உலகளவு"
]

tamil_literary_works = [
    "திருக்குறள்", "சிலப்பதிகாரம்", "மணிமேகலை", "தொல்காப்பியம்", "புறநானூறு"
]

def generate_tamil_poetry(style, theme, max_tokens=1200):
    system_prompt = """You are a renowned Tamil poet with unparalleled expertise in Tamil literature, linguistics, and culture. 
    Your task is to generate exceptional, authentic Tamil poetry that adheres strictly to the requested style and theme.
    Ensure impeccable spelling, appropriate punctuation, and create profoundly meaningful content that resonates deeply with Tamil culture and traditions.
    The English translation must precisely reflect the Tamil content, capturing all nuances, cultural references, and poetic devices.
    
    Key points to remember:
    1. Use rich, evocative language that draws from Tamil literary tradition.
    2. Incorporate culturally significant imagery, metaphors, and allusions.
    3. Ensure perfect adherence to the chosen poetic form and its rules.
    4. Create layers of meaning that invite reflection and interpretation.
    5. Balance classical elements with contemporary relevance.
    """

    style_prompts = {
        "haiku": f"""Create a Tamil haiku on '{theme}':
        1. Three lines capturing a profound moment or image.
        2. Concise, powerful language with flawless spelling and punctuation.
        3. Adhere to the 5-7-5 syllable structure, adapting it thoughtfully for Tamil.
        4. Delve deeply into the theme: {theme}, offering a unique perspective.
        5. Use imagery that resonates strongly with Tamil heritage and natural environment.
        6. Ensure each word is carefully chosen for maximum impact and meaning.""",
        
        "venba": f"""Compose a Tamil venba on '{theme}':
        1. Four lines: two கூற்று (kūṟṟu), one தாழிசை (tāḻicai), ending with சுருங்கடி (curuṅkaṭi).
        2. Follow venba meter with absolute precision: நேர் (nēr) and நிரை (nirai) patterns.
        3. Ensure the last foot of each line is இயற்சீர் (iyaṟcīr), and the final word is a single syllable.
        4. Theme: {theme} - explore it with profound insight and emotional depth.
        5. Incorporate classical Tamil concepts, drawing from works like {random.choice(tamil_literary_works)}.
        6. Use a relevant Tamil proverb or adapt one creatively: {random.choice(tamil_proverbs)}
        7. Demonstrate mastery of Tamil prosody while maintaining natural, flowing language.""",
        
        "free verse": f"""Craft a Tamil free verse poem on '{theme}':
        1. Use vivid, culturally rich imagery and metaphors deeply rooted in Tamil tradition.
        2. Skillfully incorporate classical Tamil literary devices like உவமை (uvmai) or உருவகம் (uruvakam).
        3. Experiment boldly with line breaks and punctuation for maximum emotional and aesthetic impact.
        4. Seamlessly blend traditional and modern elements to create a timeless, yet contemporary piece.
        5. Offer profound insights on the theme: {theme}, challenging conventional perspectives.
        6. Ensure the poem has philosophical depth, drawing inspiration from Tamil philosophy and literature.
        7. Pay meticulous attention to the musicality of the language, even in free verse form."""
    }

    user_prompt = style_prompts.get(style.lower(), style_prompts["free verse"])
    user_prompt += f""" 
    Provide the poem in this format:

    தமிழ் (Tamil):
    [Poem in Tamil script with perfect spelling, appropriate punctuation, and diacritical marks]

    ஒலிப்பெயர்ப்பு (Transliteration):
    [Precise Romanized transliteration with all necessary diacritical marks]

    English Translation:
    [Eloquent and accurate translation that captures the essence, cultural nuances, and poetic devices]

    Explanation:
    [Comprehensive explanation of poetic elements, cultural references, and thematic exploration. Include:
    1. Analysis of the poem's structure and adherence to the chosen style.
    2. Explanation of any wordplay, double meanings, or subtle cultural allusions.
    3. Discussion of how the poem relates to the theme: {theme}.
    4. Identification of any classical Tamil concepts or literary devices used.
    5. Reflection on the poem's cultural and philosophical significance.]
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
    # Implement basic quality checks
    checks = [
        ("தமிழ் (Tamil):" in poem, "Tamil poem is missing"),
        ("ஒலிப்பெயர்ப்பு (Transliteration):" in poem, "Transliteration is missing"),
        ("English Translation:" in poem, "English translation is missing"),
        ("Explanation:" in poem, "Explanation is missing"),
    ]
    
    issues = [issue for check, issue in checks if not check]
    
    if issues:
        st.warning("Quality check identified the following issues:")
        for issue in issues:
            st.write(f"- {issue}")
        return None
    
    return poem

st.title("Tamil Poetry Generator")

style = st.selectbox("Choose a poetry style:", ["Haiku", "Venba", "Free Verse"])
theme = st.text_input("Enter a theme for your poem:")

if st.button("Generate Poem"):
    if theme:
        with st.spinner("கவிதை உருவாக்கப்படுகிறது... (Generating poem...)"):
            poem = generate_tamil_poetry(style, theme)
            poem = quality_check(poem)
        if poem:
            st.success("கவிதை வெற்றிகரமாக உருவாக்கப்பட்டது! (Poem generated successfully!)")
            st.markdown("## Your Tamil Poem:")
            formatted_poem = format_poem(poem)
            st.markdown(formatted_poem)
    else:
        st.warning("Please enter a theme for your poem.")

st.sidebar.markdown("### About")
st.sidebar.info("This advanced app generates authentic, high-quality Tamil poetry using AI. It creates deeply meaningful, culturally rich poems with impeccable spelling and punctuation. It's a sophisticated tool for exploring Tamil poetic forms, cultural themes, and literary traditions. Created with passion by Vidhiya S B (www.x.com/Vidhiyasb)")

# Additional features
st.sidebar.markdown("### Additional Resources")
if st.sidebar.checkbox("Show Tamil Proverbs"):
    st.sidebar.write("### Tamil Proverbs")
    for proverb in tamil_proverbs:
        st.sidebar.write(f"- {proverb}")

if st.sidebar.checkbox("Show Tamil Literary Works"):
    st.sidebar.write("### Famous Tamil Literary Works")
    for work in tamil_literary_works:
        st.sidebar.write(f"- {work}")
