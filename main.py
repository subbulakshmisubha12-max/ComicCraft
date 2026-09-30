import os
import re

from fastapi import (
    FastAPI,
    Form
)

from fastapi.responses import (
    FileResponse,
    HTMLResponse,
    JSONResponse
)


from gemini import (
    GeminiUnavailableError,
    generate_outline,
    generate_story
)


from image_generator import (
    generate_image
)


from pdf_generator import (
    create_pdf
)


# ---------------------------------------
# FastAPI App
# ---------------------------------------

app = FastAPI(
    title="ComicCraft",
    description="AI Comic Story Creator",
    version="1.0"
)


# ---------------------------------------
# Home Page
# ---------------------------------------

@app.get(
    "/",
    response_class=HTMLResponse
)
async def home():

    with open(
        "index.html",
        "r",
        encoding="utf-8"
    ) as file:

        return file.read()


# ---------------------------------------
# CSS
# ---------------------------------------

@app.get(
    "/style.css"
)
async def css():

    return FileResponse(
        "style.css",
        media_type="text/css"
    )


# ---------------------------------------
# JavaScript
# ---------------------------------------

@app.get(
    "/script.js"
)
async def javascript():

    return FileResponse(
        "script.js",
        media_type="application/javascript"
    )


# ---------------------------------------
# Generate Comic
# ---------------------------------------

@app.post(
    "/generate"
)
async def generate_comic(

    story_prompt: str = Form(...),

    character_name: str = Form(...),

    setting: str = Form(...),

    tone: str = Form(...),

    art_style: str = Form(...)

):

    try:

        # -----------------------------
        # STEP 1
        # Generate outline
        # -----------------------------

        outline = generate_outline(

            story_prompt,

            character_name,

            setting,

            tone,

            art_style

        )


        # -----------------------------
        # STEP 2
        # Generate story
        # -----------------------------

        story = generate_story(

            outline,

            character_name,

            tone

        )


        # -----------------------------
        # STEP 3
        # Extract panel stories
        # -----------------------------

        story_sections = re.split(
            r"PANEL\s+\d+",
            story,
            flags=re.IGNORECASE
        )


        story_sections = [
            section.strip()
            for section in story_sections
            if section.strip()
        ]


        # -----------------------------
        # STEP 4
        # Generate images
        # -----------------------------

        panels = []


        for index, panel in enumerate(
            outline
        ):

            panel_number = (
                panel["panel"]
            )


            # Get story section
            if index < len(
                story_sections
            ):

                panel_story = (
                    story_sections[index]
                )

            else:

                panel_story = (
                    "Story content generated."
                )


            # Generate image
            image = generate_image(

                panel[
                    "image_prompt"
                ],

                panel_number,

                art_style

            )


            panels.append({

                "panel":
                    panel_number,

                "title":
                    panel["title"],

                "scene_description":
                    panel[
                        "scene_description"
                    ],

                "image":
                    image,

                "story":
                    panel_story

            })


        # -----------------------------
        # STEP 5
        # Create PDF
        # -----------------------------

        pdf_file = create_pdf(
            panels
        )


        # -----------------------------
        # STEP 6
        # Save comic data
        # -----------------------------

        # Simple HTML creation
        # using generated panel data

        html = create_comic_html(
            panels,
            pdf_file
        )


        with open(
            "comic.html",
            "w",
            encoding="utf-8"
        ) as file:

            file.write(html)


        return FileResponse(
            "comic.html",
            media_type="text/html"
        )


    except GeminiUnavailableError as error:

        return JSONResponse(

            status_code=503,

            content={
                "success": False,
                "error": str(error)
            }

        )


    except Exception as error:

        return JSONResponse(

            status_code=500,

            content={

                "success": False,

                "error":
                    str(error)

            }

        )


# ---------------------------------------
# Serve generated images
# ---------------------------------------

@app.get(
    "/image/{filename}"
)
async def get_image(
    filename: str
):

    filepath = os.path.join(
        os.getcwd(),
        filename
    )


    if not os.path.exists(
        filepath
    ):

        return JSONResponse(

            status_code=404,

            content={
                "error":
                    "Image not found"
            }

        )


    return FileResponse(
        filepath
    )


# ---------------------------------------
# Serve PDF
# ---------------------------------------

@app.get(
    "/download/{filename}"
)
async def download_pdf(
    filename: str
):

    filepath = os.path.join(
        os.getcwd(),
        filename
    )


    if not os.path.exists(
        filepath
    ):

        return JSONResponse(

            status_code=404,

            content={
                "error":
                    "PDF not found"
            }

        )


    return FileResponse(

        filepath,

        media_type="application/pdf",

        filename=filename

    )


# ---------------------------------------
# Create Comic HTML
# ---------------------------------------

def create_comic_html(
    panels,
    pdf_file
):

    panel_html = ""


    for panel in panels:

        panel_html += f"""

        <div class="panel">

            <h2>
                Panel {panel["panel"]}:
                {panel["title"]}
            </h2>

            <img
                src="/image/{panel["image"]}"
                alt="Comic Panel"
            >

            <div class="scene">

                <strong>
                    Scene:
                </strong>

                <p>
                    {panel["scene_description"]}
                </p>

            </div>

            <div class="story">

                <strong>
                    Story:
                </strong>

                <p>
                    {panel["story"]}
                </p>

            </div>

        </div>

        """


    html = f"""

<!DOCTYPE html>

<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width,
        initial-scale=1.0"
    >

    <title>
        ComicCraft - Your Comic
    </title>

    <link
        rel="stylesheet"
        href="/style.css"
    >

</head>


<body>

    <div class="preview-container">

        <div class="preview-header">

            <h1>
                🎨 Your Comic
            </h1>

            <p>
                AI Generated Comic Story
            </p>

        </div>


        {panel_html}


        <div class="buttons">

            <a
                href="/download/{pdf_file}"
                class="download-btn"
            >
                📥 Download PDF
            </a>


            <a
                href="/"
                class="back-btn"
            >
                🔄 Create Another
            </a>

        </div>

    </div>

</body>

</html>

"""


    return html


# ---------------------------------------
# Run
# ---------------------------------------

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )