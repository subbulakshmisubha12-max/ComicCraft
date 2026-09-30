import os

from fpdf import FPDF


def create_pdf(
    panels
):
    """
    Create PDF from comic panels.
    """

    filename = "comic.pdf"

    filepath = os.path.join(
        os.getcwd(),
        filename
    )


    pdf = FPDF(
        orientation="P",
        unit="mm",
        format="A4"
    )


    pdf.set_auto_page_break(
        auto=True,
        margin=15
    )


    for panel in panels:

        pdf.add_page()


        # Title
        pdf.set_font(
            "Arial",
            "B",
            20
        )


        title = (
            f"Panel {panel['panel']}: "
            f"{panel['title']}"
        )


        pdf.cell(
            0,
            12,
            title,
            ln=True
        )


        # Image
        image_path = os.path.join(
            os.getcwd(),
            panel["image"]
        )


        if os.path.exists(
            image_path
        ):

            pdf.image(
                image_path,
                x=10,
                y=30,
                w=190
            )


        # Move cursor
        pdf.set_y(145)


        # Scene
        pdf.set_font(
            "Arial",
            "B",
            12
        )


        pdf.cell(
            0,
            8,
            "Scene",
            ln=True
        )


        pdf.set_font(
            "Arial",
            "",
            11
        )


        scene = (
            panel["scene_description"]
        )


        scene = scene.encode(
            "latin-1",
            "replace"
        ).decode(
            "latin-1"
        )


        pdf.multi_cell(
            0,
            6,
            scene
        )


        pdf.ln(5)


        # Story
        pdf.set_font(
            "Arial",
            "B",
            12
        )


        pdf.cell(
            0,
            8,
            "Story",
            ln=True
        )


        pdf.set_font(
            "Arial",
            "",
            10
        )


        story = panel["story"]


        story = story.encode(
            "latin-1",
            "replace"
        ).decode(
            "latin-1"
        )


        pdf.multi_cell(
            0,
            6,
            story
        )


    pdf.output(
        filepath
    )


    return filename