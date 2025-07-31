from fpdf import FPDF

def save_pdf(text, title="Appunti Universitari", filename="appunti.pdf"):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_title(title)
    pdf.set_font("Arial", size=12)

    blocks = text.split("\n\n")
    for idx, block in enumerate(blocks, start=1):
        pdf.set_font("Arial", style="B", size=12)
        pdf.cell(0, 10, f"- Blocco {idx}", ln=True)
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, block)
        pdf.ln(5)

    pdf.output(filename)
    return filename
