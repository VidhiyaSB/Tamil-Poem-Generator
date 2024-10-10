



```python
```python
import streamlit as st
from groq import Groq
import re
import random
import json
import base64
import logging
import gtts
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Access the API key from Streamlit secrets
llama_api_key = st.secrets["api_keys"]["LLAMA_API_KEY"]

# Initialize the Groq client
client = Groq(api_key=llama_api_key)

# Set up logging
logging.basicConfig(filename='tamil_poetry_generator.log', level=logging.INFO)

# Tamil literature resources
tamil_proverbs = [
    "அகத்தின் அழகு முகத்தில் தெரியும்",
    "யானை இருந்தாலும் குதிரை இருந்தாலும் ஓட்டுநர் திறமையே முக்கியம்",
    "கற்றது கைமண் அளவு, கல்லாதது உலகளவு"
]

tamil_literary_works = [
    "திருக்குறள்", "சிலப்பதிகாரம்", "மணிமேகலை", "தொல்காப்பியம்", "புறநானூறு"
]

@st.cache(ttl=3600)
def generate_tamil_poetry(style, theme, tone=None, length=None, max_tokens=1500):
    system_prompt = """You are a renowned Tamil poet with unparalleled expertise in Tamil literature, linguistics, and culture. 
    Your task is to generate exceptional, authentic Tamil poetry that adheres strictly to the requested style, theme, tone, and length.
    Ensure impeccable spelling, appropriate punctuation, and create profoundly meaningful content that resonates deeply with Tamil culture and traditions.
    The English translation must precisely reflect the Tamil content, capturing all nuances, cultural references, and poetic devices.
    
    Key points to remember:
    1. Use rich, evocative language that draws from Tamil literary tradition.
    2. Incorporate culturally significant imagery, metaphors, and allusions.
    3. Ensure perfect adherence to the chosen poetic form and its rules.
    4. Create layers of meaning that invite reflection and interpretation.
    5. Balance classical elements with contemporary relevance.
    6. Adapt the tone and length as specified by the user.
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
    
    if tone:
        user_prompt += f"\n8. Maintain a {tone} tone throughout the poem."
    
    if length:
        user_prompt += f"\n9. Aim for a {length} poem in terms of lines or stanzas."

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
        logging.error(f"Error in poem generation: {str(e)}")
        st.error("An error occurred while generating the poem. Please try again later.")
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
    checks = [
        ("தமிழ் (Tamil):" in poem, "Tamil poem is missing"),
        ("ஒலிப்பெயர்ப்பு (Transliteration):" in poem, "Transliteration is missing"),
        ("English Translation:" in poem, "English translation is missing"),
        ("Explanation:" in poem, "Explanation is missing"),
        (len(poem.split()) >= 50, "Poem seems too short"),
        (any(word in poem.lower() for word in ["புறநானூறு", "திருக்குறள்", "சிலப்பதிகாரம்"]), "No classical Tamil references detected"),
        (re.search(r'[ஆஈஊஏஐஓஔ]', poem), "No long vowels found, poem might lack depth"),
    ]
    
    issues = [issue for check, issue in checks if not check]
    
    if issues:
        st.warning("Quality check identified the following issues:")
        for issue in issues:
            st.write(f"- {issue}")
        return None
    
    return poem

def generate_audio(text):
    tts = gtts.gTTS(text, lang='ta')
    audio_file = "poem_audio.mp3"
    tts.save(audio_file)
    return audio_file

def save_poem(poem):
    poems = json.loads(st.session_state.get('saved_poems', '[]'))
    poems.append(poem)
    st.session_state['saved_poems'] = json.dumps(poems)

def get_shareable_link(poem):
    encoded_poem = base64.b64encode(poem.encode()).decode()
    return f"https://tamil-poem-and-haiku-generator.streamlit.app/?poem={encoded_poem}"

def rate_poem(poem_id, rating):
    # Implement rating storage logic (e.g., database update)
    st.success(f"Thank you for rating this poem {rating}/5 stars!")

# Main app
try:
    st.title("Advanced Tamil Poetry Generator")

    style = st.selectbox("Choose a poetry style:", ["Haiku", "Venba", "Free Verse"])
    theme = st.text_input("Enter a theme for your poem:")
    tone = st.selectbox("Select the tone of the poem:", ["None", "Joyful", "Melancholic", "Philosophical", "Romantic", "Patriotic"])
    length = st.selectbox("Choose the length of the poem:", ["None", "Short (1-4 lines)", "Medium (5-12 lines)", "Long (13+ lines)"])

    if 'generated_poems' not in st.session_state:
        st.session_state.generated_poems = {}

    if st.button("Generate Poem"):
        if theme:
            poem_key = f"{style}_{theme}_{tone}_{length}"
            if poem_key in st.session_state.generated_poems:
                poem = st.session_state.generated_poems[poem_key]
            else:
                with st.spinner("கவிதை உருவாக்கப்படுகிறது... (Generating poem...)"):
                    poem = generate_tamil_poetry(style, theme, tone if tone != "None" else None, length if length != "None" else None)
                    poem = quality_check(poem)
                    if poem:
                        st.session_state.generated_poems[poem_key] = poem
            
            if poem:
                st.success("கவிதை வெற்றிகரமாக உருவாக்கப்பட்டது! (Poem generated successfully!)")
                st.markdown("## Your Tamil Poem:")
                formatted_poem = format_poem(poem)
                st.markdown(formatted_poem)

                st.markdown("## Listen to Your Poem:")
                tamil_text = re.search(r'தமிழ் \(Tamil\):(.*?)ஒலிப்பெயர்ப்பு', poem, re.DOTALL)
                if tamil_text:
                    audio_file = generate_audio(tamil_text.group(1).strip())
                    st.audio(audio_file)
                else:
                    st.warning("Could not extract Tamil text for audio generation.")

                if st.button("Save Poem"):
                    save_poem(poem)
                    st.success("Poem saved successfully!")
                
                share_link = get_shareable_link(poem)
                st.markdown(f"Share your poem: [Click here]({share_link})")

                st.markdown("## Rate this poem:")
                rating = st.slider("How would you rate this poem?", 1, 5, 3)
                if st.button("Submit Rating"):
                    rate_poem(poem_key, rating)
                
                feedback = st.text_area("Provide feedback (optional):")
                if st.button("Submit Feedback"):
                    # Implement feedback storage logic
                    st.success("Thank you for your feedback!")

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

    if st.sidebar.checkbox("View Saved Poems"):
        saved_poems = json.loads(st.session_state.get('saved_poems', '[]'))
        for i, saved_poem in enumerate(saved_poems):
            st.sidebar.markdown(f"### Poem {i+1}")
            st.sidebar.text(saved_poem[:100] + "...")  # Display a preview

except Exception as e:
    logging.error(f"Unhandled exception in main app: {str(e)}")
    st.error("An unexpected error occurred. Please try refreshing the page.")


