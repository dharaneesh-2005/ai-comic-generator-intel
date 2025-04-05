import os
import json
from comic_generation.generate_panels import generate_panels
from comic_generation.stability_ai import text_to_image
from comic_generation.add_text import add_text_to_panel
from comic_generation.create_strip import create_strip
import streamlit as st
from PIL import Image

# Setup output directory and API keys
os.makedirs("output", exist_ok=True)

# Safely retrieve API keys from Streamlit secrets
api_key = st.secrets.get("openai", {}).get("api_key")
stability_api_key = os.getenv("STABILITY_KEY")

if api_key:
    os.environ["OPENAI_API_KEY"] = api_key
else:
    st.warning("OpenAI API key is missing in Streamlit secrets!", icon="⚠️")

# Page setup
favicon = Image.open("favicon.png")
st.set_page_config(
    page_title="GenAI Demo | Trigent AXLR8 Labs",
    page_icon=favicon,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar branding
logo_html = """
<style>
    [data-testid="stSidebarNav"] {
        background-image: url(https://trigent.com/wp-content/uploads/Trigent_Axlr8_Labs.png);
        background-repeat: no-repeat;
        background-position: 20px 20px;
        background-size: 80%;
    }
</style>
"""
st.sidebar.markdown(logo_html, unsafe_allow_html=True)
st.title("INTEL UNNATI PROBLEM STATEMENT - 06")

# API key confirmation
if api_key:
    success_message_html = """
    <span style='color:green; font-weight:bold;'>TEAM 1 AI COMIC GENERATOR    """
    st.markdown(success_message_html, unsafe_allow_html=True)
    openai_api_key = api_key
else:
    openai_api_key = st.text_input('Enter your OPENAI_API_KEY: ', type='password')
    if not openai_api_key:
        st.warning('Please, enter your OPENAI_API_KEY', icon='⚠️')
        st.stop()
    else:
        os.environ["OPENAI_API_KEY"] = openai_api_key
        st.success('Get your comic ready in minutes!', icon='👉')

# User input
SCENARIO = st.text_area(
    "Enter your Story and the characters",
    """Characters: A IT industry Manager named Andy and Couple of Software developers with a Laptop.
The manager is a super guy who manages all his Developers.
Once there was a super powerful task which the manager assigned to one of his new developers and the developer was able to do it and the Manager was amazed and awarded him with a USA ticket.""",
)

STYLE = st.text_input("Enter the style of your characters", "Indian comic, coloured")

if st.button("Generate"):
    with st.spinner("Making a comic for you..."):
        try:
            st.info(f"Generating panels in style: **{STYLE}**", icon="🎨")
            panels = generate_panels(SCENARIO)

            if not panels or not isinstance(panels, list):
                st.error("Panel generation failed or returned invalid data.")
                st.stop()

            with open("output/panels.json", "w") as outfile:
                json.dump(panels, outfile)

            panel_images = []

            for i, panel in enumerate(panels, start=1):
                description = panel.get("description", "A scene in the comic")
                panel_text = panel.get("text", "")
                panel_number = panel.get("number", i)  # Fallback to index if 'number' is missing

                panel_prompt = f"{description}, cartoon box, {STYLE}"
                textData = f"🎬 Generate panel {panel_number} with prompt: {panel_prompt}"
                st.markdown(textData)

                panel_image = text_to_image(panel_prompt)
                panel_image_with_text = add_text_to_panel(panel_text, panel_image)
                panel_images.append(panel_image_with_text)

            if panel_images:
                res = create_strip(panel_images)
                st.image(res, caption="Here is your comic strip!", use_container_width=True)
            else:
                st.error("No images were generated. Please check your inputs.")

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")


