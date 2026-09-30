import os
import json
import re
import time

from dotenv import load_dotenv
from google import genai


# Load .env
load_dotenv()


# Get API key
API_KEY = os.getenv("GEMINI_API_KEY")


if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found in .env file"
    )


# Gemini client
client = genai.Client(
    api_key=API_KEY
)


# Current text model
TEXT_MODEL = "gemini-3.8-flash"


class GeminiUnavailableError(RuntimeError):
    pass


def _is_retryable_error(error):
    retryable_status_codes = {429, 500, 502, 503, 504}
    retryable_windows_errors = {10053, 10054, 10060}
    retryable_transport_error_names = {
        "RemoteProtocolError",
        "ConnectError",
        "ReadError",
        "WriteError",
        "ConnectTimeout",
        "ReadTimeout",
        "WriteTimeout",
        "PoolTimeout",
        "NetworkError"
    }
    pending_errors = [error]
    checked_errors = set()

    while pending_errors:
        current = pending_errors.pop()
        if id(current) in checked_errors:
            continue
        checked_errors.add(id(current))

        status_code = getattr(current, "code", None)
        if status_code is None:
            status_code = getattr(
                getattr(current, "response", None),
                "status_code",
                None
            )

        if status_code in retryable_status_codes:
            return True

        if type(current).__name__ in retryable_transport_error_names:
            return True

        if isinstance(current, (ConnectionError, TimeoutError)):
            return True

        if isinstance(current, OSError) and (
            getattr(current, "winerror", None) in retryable_windows_errors
            or current.errno in retryable_windows_errors
        ):
            return True

        if current.__cause__ is not None:
            pending_errors.append(current.__cause__)
        if current.__context__ is not None:
            pending_errors.append(current.__context__)

    return False


def call_gemini_with_retry(request):
    for attempt in range(3):
        try:
            return request()
        except Exception as error:
            if not _is_retryable_error(error):
                raise

            if attempt == 2:
                raise GeminiUnavailableError(
                    "Gemini's service or network connection is temporarily unavailable. Please try again in a minute."
                ) from error

            time.sleep(2 ** attempt)


def call_gemini_with_fallback(requests):
    for request in requests:
        try:
            return call_gemini_with_retry(request)
        except GeminiUnavailableError:
            continue

    raise GeminiUnavailableError(
        "Gemini's text models are temporarily busy. Please try again in a minute."
    )


def _generate_text(prompt):
    models = (
        TEXT_MODEL,
        "gemini-3.7-flash",
        "gemini-3.6-flash",
        "gemini-3.5-flash"
    )
    requests = [
        lambda model=model: client.models.generate_content(
            model=model,
            contents=prompt
        )
        for model in models
    ]

    return call_gemini_with_fallback(requests)


def clean_json(text):
    """
    Remove markdown code fences from Gemini response.
    """

    text = text.strip()

    text = re.sub(
        r"```json",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"```",
        "",
        text
    )

    return text.strip()


def generate_outline(
    story_prompt,
    character_name,
    setting,
    tone,
    art_style
):
    """
    Generate a 5-panel comic outline.
    """

    prompt = f"""
You are an expert comic story planner.

Create a continuous 5-panel comic story.

USER INPUT:

Story idea:
{story_prompt}

Main character:
{character_name}

Setting:
{setting}

Tone:
{tone}

Art style:
{art_style}


IMPORTANT:

- Create exactly 5 panels.
- The same main character must appear in all panels.
- Each panel must continue the previous panel.
- Keep the story simple and interesting.
- Create a detailed image prompt for every panel.

Return ONLY valid JSON.

Use exactly this structure:

[
  {{
    "panel": 1,
    "title": "Panel title",
    "scene_description": "Scene description",
    "image_prompt": "Detailed image generation prompt"
  }},
  {{
    "panel": 2,
    "title": "Panel title",
    "scene_description": "Scene description",
    "image_prompt": "Detailed image generation prompt"
  }},
  {{
    "panel": 3,
    "title": "Panel title",
    "scene_description": "Scene description",
    "image_prompt": "Detailed image generation prompt"
  }},
  {{
    "panel": 4,
    "title": "Panel title",
    "scene_description": "Scene description",
    "image_prompt": "Detailed image generation prompt"
  }},
  {{
    "panel": 5,
    "title": "Panel title",
    "scene_description": "Scene description",
    "image_prompt": "Detailed image generation prompt"
  }}
]
"""


    response = _generate_text(prompt)


    result = clean_json(
        response.text
    )


    try:

        outline = json.loads(result)

    except json.JSONDecodeError:

        raise ValueError(
            "Gemini returned invalid JSON."
        )


    if not isinstance(
        outline,
        list
    ):

        raise ValueError(
            "Invalid comic outline."
        )


    if len(outline) != 5:

        raise ValueError(
            "Comic outline must contain 5 panels."
        )


    return outline


def generate_story(
    outline,
    character_name,
    tone
):
    """
    Generate narration, dialogue and captions.
    """

    outline_text = ""


    for panel in outline:

        outline_text += f"""

Panel {panel["panel"]}

Title:
{panel["title"]}

Scene:
{panel["scene_description"]}

"""


    prompt = f"""
You are a professional comic writer.

Create narration, dialogue and captions
for a 5-panel comic.

Character:
{character_name}

Tone:
{tone}

Comic outline:
{outline_text}


For every panel provide:

PANEL 1
Narration:
Dialogue:
Caption:

PANEL 2
Narration:
Dialogue:
Caption:

PANEL 3
Narration:
Dialogue:
Caption:

PANEL 4
Narration:
Dialogue:
Caption:

PANEL 5
Narration:
Dialogue:
Caption:


Rules:

- Keep dialogue short.
- Make the story continuous.
- Make it suitable for a comic.
- Do not add extra panels.
"""


    response = _generate_text(prompt)


    return response.text.strip()