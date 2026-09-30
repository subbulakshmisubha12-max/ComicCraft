import os
import base64

from dotenv import load_dotenv
from google import genai
from gemini import call_gemini_with_retry


# Load environment
load_dotenv()


API_KEY = os.getenv(
    "GEMINI_API_KEY"
)


if not API_KEY:

    raise ValueError(
        "GEMINI_API_KEY not found."
    )


# Gemini client
client = genai.Client(
    api_key=API_KEY
)


IMAGE_MODEL = (
    "gemini-3.1-flash-image"
)


def generate_image(
    prompt,
    panel_number,
    art_style
):
    """
    Generate an image for one comic panel.
    """

    full_prompt = f"""
Create a high-quality comic book illustration.

Style:
{art_style}

Scene:
{prompt}

Requirements:

- Clear main character
- Consistent character appearance
- Strong storytelling composition
- Detailed background
- Cinematic lighting
- Comic illustration style
- No watermark-like text
- No speech bubbles
- No captions
"""


    interaction = call_gemini_with_retry(
        lambda: client.interactions.create(
            model=IMAGE_MODEL,
            input=full_prompt,
            response_format={
                "type": "image",
                "aspect_ratio": "16:9",
                "image_size": "1K"
            }
        )
    )


    image_data = (
        interaction.output_image.data
    )


    # Decode base64
    image_bytes = base64.b64decode(
        image_data
    )


    filename = (
        f"panel_{panel_number}.png"
    )


    filepath = os.path.join(
        os.getcwd(),
        filename
    )


    with open(
        filepath,
        "wb"
    ) as file:

        file.write(
            image_bytes
        )


    return filename