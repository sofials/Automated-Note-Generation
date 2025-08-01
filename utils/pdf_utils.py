from fpdf import FPDF
import os
import logging

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFGenerationError(Exception):
    """Eccezione personalizzata per errori di generazione PDF"""
    pass

def validate_text_for_pdf(text):
    """Valida il testo per la generazione PDF"""
    if not text or not isinstance(text, str):
        return False, "Testo non valido"
    
    if len(text.strip()) < 10:
        return False, "Testo troppo corto"
    
    # Verifica caratteri problematici
    problematic_chars = ['\x00', '\x01', '\x02', '\x03', '\x04', '\x05', '\x06', '\x07']
    for char in problematic_chars:
        if char in text:
            return False, f"Testo contiene caratteri non validi"
    
    return True, "Testo valido"

def sanitize_text_for_pdf(text):
    """Sanitizza il testo per la generazione PDF"""
    if not text:
        return ""
    
    # Rimuovi caratteri problematici
    problematic_chars = ['\x00', '\x01', '\x02', '\x03', '\x04', '\x05', '\x06', '\x07']
    for char in problematic_chars:
        text = text.replace(char, '')
    
    # Normalizza line breaks
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # Limita lunghezza linee
    lines = text.split('\n')
    sanitized_lines = []
    for line in lines:
        if len(line) > 200:  # Limite ragionevole per PDF
            sanitized_lines.append(line[:197] + "...")
        else:
            sanitized_lines.append(line)
    
    return '\n'.join(sanitized_lines)

def save_pdf(text, title="Appunti Universitari", filename="appunti.pdf"):
    """
    Salva il testo in un file PDF con gestione errori robusta
    """
    try:
        # Validazione input
        is_valid, error_msg = validate_text_for_pdf(text)
        if not is_valid:
            raise PDFGenerationError(f"Testo non valido: {error_msg}")
        
        # Sanitizza testo
        sanitized_text = sanitize_text_for_pdf(text)
        if not sanitized_text:
            raise PDFGenerationError("Testo vuoto dopo sanitizzazione")
        
        # Valida parametri
        if not title or not isinstance(title, str):
            title = "Appunti Universitari"
        
        if not filename or not isinstance(filename, str):
            filename = "appunti.pdf"
        
        # Assicurati che il filename abbia estensione .pdf
        if not filename.lower().endswith('.pdf'):
            filename += '.pdf'
        
        # Crea PDF
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        # Imposta metadati
        try:
            pdf.set_title(title[:100])  # Limita lunghezza titolo
        except Exception as e:
            logger.warning(f"Errore impostazione titolo PDF: {e}")
        
        # Imposta font
        try:
            pdf.set_font("Arial", size=12)
        except Exception as e:
            logger.warning(f"Errore impostazione font: {e}")
            # Fallback a font di default
            pdf.set_font("Helvetica", size=12)
        
        # Dividi testo in blocchi
        blocks = sanitized_text.split("\n\n")
        
        for idx, block in enumerate(blocks, start=1):
            try:
                # Aggiungi titolo blocco
                pdf.set_font("Arial", style="B", size=12)
                block_title = f"Blocco {idx}"
                pdf.cell(0, 10, block_title, ln=True)
                
                # Aggiungi contenuto
                pdf.set_font("Arial", size=12)
                
                # Gestisci testo lungo
                if len(block) > 1000:
                    # Dividi in paragrafi più piccoli
                    sentences = block.split('. ')
                    current_paragraph = ""
                    
                    for sentence in sentences:
                        if len(current_paragraph) + len(sentence) < 500:
                            current_paragraph += sentence + ". "
                        else:
                            if current_paragraph:
                                pdf.multi_cell(0, 10, current_paragraph.strip())
                                current_paragraph = sentence + ". "
                    
                    if current_paragraph:
                        pdf.multi_cell(0, 10, current_paragraph.strip())
                else:
                    pdf.multi_cell(0, 10, block)
                
                pdf.ln(5)
                
            except Exception as e:
                logger.error(f"Errore aggiunta blocco {idx}: {e}")
                # Aggiungi messaggio di errore nel PDF
                pdf.set_font("Arial", style="I", size=10)
                pdf.multi_cell(0, 10, f"[Errore elaborazione blocco {idx}]")
                pdf.set_font("Arial", size=12)
        
        # Salva file
        try:
            pdf.output(filename)
            
            # Verifica che il file sia stato creato
            if not os.path.exists(filename):
                raise PDFGenerationError("File PDF non creato")
            
            file_size = os.path.getsize(filename)
            if file_size == 0:
                raise PDFGenerationError("File PDF vuoto")
            
            logger.info(f"PDF generato con successo: {filename} ({file_size} bytes)")
            return filename
            
        except Exception as e:
            raise PDFGenerationError(f"Errore salvataggio PDF: {e}")
    
    except Exception as e:
        logger.error(f"Errore generazione PDF: {e}")
        raise PDFGenerationError(f"Impossibile generare PDF: {e}")

def create_simple_pdf(text, filename="output.pdf"):
    """
    Crea un PDF semplice come fallback
    """
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)
        
        # Aggiungi testo semplice
        lines = text.split('\n')
        for line in lines[:50]:  # Limita a 50 linee
            if line.strip():
                pdf.cell(0, 10, line[:100], ln=True)  # Limita lunghezza linea
        
        pdf.output(filename)
        return filename
        
    except Exception as e:
        logger.error(f"Errore creazione PDF semplice: {e}")
        return None
