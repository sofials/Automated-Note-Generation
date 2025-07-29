from fpdf import FPDF

def save_pdf(text, title="Appunti Universitari", filename="appunti.pdf"):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.set_title(title)

    lines = text.split('\n')
    for line in lines:
        pdf.multi_cell(0, 10, line)

    pdf.output(filename)
    return filename
