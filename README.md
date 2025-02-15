# Instagram Caption Generator

Instagram Caption Generator is a Streamlit-based web application that uses the ROQ GPT-4 Vision API to analyze an image and generate a detailed description along with 10 Instagram caption suggestions. The generated captions are displayed in two columns, and each caption can be copied to your clipboard with a single click.

## Features

- **Image Analysis:** Upload an image and have the app generate a detailed, 8-sentence description in a natural, flattering tone.
- **Caption Suggestions:** Receive 10 Instagram caption options inspired by pop culture and song lyrics.
- **Easy Copy:** Each caption option comes with a "Copy" button to quickly copy the caption text.
- **Refresh Suggestions:** Regenerate caption suggestions without re-uploading the image.

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/instagram-caption-generator.git
   cd instagram-caption-generator

2. **Create and Activate a Virtual Environment (optional but recommended):**

   $ python3 -m venv venv
   $ source venv/bin/activate

3. **Install Dependencies:**

   $ pip install -r requirements.txt

4. **Configure Environment Variables:**

   Create a file named .env in the project root with your ROQ API key:

   GROQ_API_KEY=your_api_key_here

5. **Set up .gitignore:**

   Create a file named .gitignore in the project root with the following content:

   uploaded_images/
   .env
