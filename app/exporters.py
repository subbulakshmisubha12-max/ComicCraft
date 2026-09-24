from fpdf import FPDF

def save_pdf(layout):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    for panel in layout:
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=panel["title"], ln=True)
        pdf.multi_cell(0, 10, panel["desc"])
        pdf.image(panel["image"], x=10, y=40, w=100)
    path = "static/exports/comic.pdf"
    pdf.output(path)
    return path
