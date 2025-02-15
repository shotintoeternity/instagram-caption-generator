import streamlit as st
import base64
import re
import os
import logging
from groq import Groq
from dotenv import load_dotenv
from html import escape
import streamlit.components.v1 as components

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    filename="app.log",
    filemode="a",
    format="%(asctime)s %(levelname)s:%(message)s"
)
logger = logging.getLogger()

# Load GROQ API key from .env file
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    st.error("Please set GROQ_API_KEY in your .env file.")
    st.stop()

# Initialize the GROQ client
client = Groq(api_key=GROQ_API_KEY)

def generate_caption(image_bytes):
    # Encode the image as base64 and build a data URI (assuming JPEG)
    encoded_image = base64.b64encode(image_bytes).decode("utf-8")
    data_uri = f"data:image/jpeg;base64,{encoded_image}"
    
    prompt_text = (
        "Please analyze the attached image and generate a detailed, long and flowing description that is exactly 8 sentences long. "
        "The description should capture everything you see in a natural, flattering tone, complimenting the interesting qualities of the photo "
        "and emphasizing its main focus. "
        "Then produce a primary Instagram caption as a single, succinct phrase and 10 additional caption options "
        "(each a full descriptive phrase in sentence case, without multiple sentences or dashes), inspired by pop culture and song lyrics when appropriate, "
        "and occasionally include emojis. "
        "Format your response exactly as follows:\n\n"
        "Description: <long, flattering description>\n"
        "Main Caption: <primary caption>\n"
        "Captions:\n"
        "1. <caption option 1>\n"
        "2. <caption option 2>\n"
        "3. <caption option 3>\n"
        "4. <caption option 4>\n"
        "5. <caption option 5>\n"
        "6. <caption option 6>\n"
        "7. <caption option 7>\n"
        "8. <caption option 8>\n"
        "9. <caption option 9>\n"
        "10. <caption option 10>"
    )
    
    response = client.chat.completions.create(
        model="llama-3.2-90b-vision-preview",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt_text},
                {"type": "image_url", "image_url": {"url": data_uri}}
            ]
        }],
        temperature=1,
        max_tokens=1500,
        top_p=1,
        stream=False,
        stop=None
    )
    return response.choices[0].message.content.strip()

def sentence_case(text):
    if not text:
        return text
    return text[0].upper() + text[1:].lower()

def remove_surrounding_quotes(text):
    text = text.strip()
    if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
        return text[1:-1].strip()
    return text

# Create directory for uploaded images
upload_dir = "uploaded_images"
os.makedirs(upload_dir, exist_ok=True)

st.title("Instagram AI Caption Maker")

# Inject a global JavaScript function for copying text
st.markdown(
    """
    <script>
    function copyText(text) {
        navigator.clipboard.writeText(text).then(function() {
            alert("Instagram caption copied successfully!");
        }, function(err) {
            alert("Failed to copy: " + err);
        });
    }
    </script>
    """,
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader("Upload a JPG, PNG, or WEBP image", type=["jpg", "jpeg", "png", "webp"])
if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    st.image(file_bytes, caption="Uploaded Image", use_container_width=True)
    
    # Save the uploaded image locally
    file_path = os.path.join(upload_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(file_bytes)
    logger.info(f"File uploaded: {uploaded_file.name}")
    
    with st.spinner("Generating description and captions..."):
        output = generate_caption(file_bytes)
    
    # Split output into head and captions parts using "Captions:" (case-insensitive)
    match = re.search(r'captions:', output, re.IGNORECASE)
    if match:
        head = output[:match.start()]
        captions_part = output[match.end():]
    else:
        head, captions_part = output, ""
    
    # Parse head for description and main caption
    description = ""
    main_caption = ""
    for line in head.splitlines():
        if line.lower().startswith("description:"):
            description = line.split(":", 1)[1].strip()
        elif line.lower().startswith("main caption:"):
            main_caption = line.split(":", 1)[1].strip()
    if not description:
        description = " ".join([l.strip() for l in head.splitlines() if not l.lower().startswith("main caption:")]).strip()
    
    # Parse caption options: each line starting with a number and a dot
    caption_options = []
    for line in captions_part.splitlines():
        line = line.strip()
        for i in range(1, 11):
            if line.startswith(f"{i}."):
                parts = line.split(".", 1)
                if len(parts) == 2:
                    cap = parts[1].strip()
                    # Force caption option into sentence case and remove extra quotes.
                    cap = sentence_case(remove_surrounding_quotes(cap))
                    caption_options.append(cap)
                break
    
    logger.info("Generated Description: " + description)
    for idx, cap in enumerate(caption_options, start=1):
        logger.info(f"Caption {idx}: {cap}")
    
    st.markdown("## Generated Description")
    st.markdown(f"**{description}**")
    
    st.markdown("## Generated Captions")
    st.markdown("**Caption Options:**")
    # Display caption options in two columns (5 per column)
    half = len(caption_options) // 2
    col1, col2 = st.columns(2)
    
    def render_copy_button(text, elem_id):
        safe_text = remove_surrounding_quotes(escape(text))
        html_code = f"""
        <div>
            <textarea id="{elem_id}" style="position: absolute; left: -1000px;">{safe_text}</textarea>
            <button onclick="document.getElementById('{elem_id}').select(); document.execCommand('copy'); alert('Instagram caption copied successfully!');" style="padding:4px 8px;">Copy</button>
        </div>
        """
        return html_code
    
    with col1:
        for idx, cap in enumerate(caption_options[:half], start=1):
            element_id = f"copy_elem_{idx}"
            components.html(f"<div style='margin-bottom: 5px; font-weight: bold;'>{idx}. {cap} {render_copy_button(cap, element_id)}</div>", height=80)
    with col2:
        for idx, cap in enumerate(caption_options[half:], start=half+1):
            element_id = f"copy_elem_{idx}"
            components.html(f"<div style='margin-bottom: 5px; font-weight: bold;'>{idx}. {cap} {render_copy_button(cap, element_id)}</div>", height=80)
