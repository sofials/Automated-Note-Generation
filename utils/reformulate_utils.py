from transformers import pipeline
import re
import time
import logging

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Variabile globale per il modello (caricamento lazy)
_reformulator = None

def get_reformulator():
    """Carica il modello di riformulazione in modo lazy"""
    global _reformulator
    if _reformulator is None:
        try:
            logger.info("Caricamento modello di riformulazione...")
            _reformulator = pipeline("text2text-generation", model="google/flan-t5-large")
            logger.info("Modello caricato con successo")
        except Exception as e:
            logger.error(f"Errore caricamento modello: {e}")
            raise RuntimeError(f"Impossibile caricare modello di riformulazione: {e}")
    return _reformulator

def clean_text(text):
    """Pulisce il testo da elementi del parlato"""
    if not text or not isinstance(text, str):
        return ""
    
    # Rimuovi elementi del parlato
    text = re.sub(r'\b(ehm+|mmm+|tipo|cioè|insomma|praticamente)\b', '', text, flags=re.IGNORECASE)
    
    # Rimuovi ripetizioni di punteggiatura
    text = re.sub(r'(\.\s*){2,}', '. ', text)
    text = re.sub(r'(\,\s*){2,}', ', ', text)
    text = re.sub(r'(\?\s*){2,}', '? ', text)
    text = re.sub(r'(\!\s*){2,}', '! ', text)
    
    # Normalizza spazi
    text = re.sub(r'\s{2,}', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()

def split_chunks(text, max_chars=1500):
    """Divide il testo in chunks gestibili"""
    if not text:
        return []
    
    # Assicurati che max_chars sia ragionevole
    max_chars = max(500, min(max_chars, 3000))
    
    chunks = []
    current_chunk = ""
    
    # Dividi per paragrafi prima
    paragraphs = text.split('\n\n')
    
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
            
        # Se il paragrafo è troppo lungo, dividilo
        if len(paragraph) > max_chars:
            # Dividi per frasi
            sentences = re.split(r'[.!?]+', paragraph)
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                    
                if len(current_chunk) + len(sentence) < max_chars:
                    current_chunk += sentence + ". "
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence + ". "
        else:
            # Se il paragrafo si adatta al chunk corrente
            if len(current_chunk) + len(paragraph) < max_chars:
                current_chunk += paragraph + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph + "\n\n"
    
    # Aggiungi l'ultimo chunk
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def reformulate_transcription(text, formal_level="Medio", use_sections=False):
    """
    Riformula la trascrizione in appunti scritti con gestione errori robusta
    """
    if not text or not isinstance(text, str):
        return "", []
    
    try:
        # Pulisci il testo
        cleaned = clean_text(text)
        if not cleaned:
            return "", []
        
        # Valida livello di formalità
        valid_levels = ["Medio", "Alto", "Molto Alto"]
        if formal_level not in valid_levels:
            formal_level = "Medio"
        
        # Dividi in chunks
        chunks = split_chunks(cleaned)
        if not chunks:
            return "", []
        
        # Ottieni il modello
        reformulator = get_reformulator()
        
        notes_by_block = []
        final_notes = []
        
        for i, chunk in enumerate(chunks):
            try:
                # Crea prompt appropriato
                prompt = f"Converti il seguente testo parlato in appunti scritti, tono {formal_level.lower()}."
                
                if use_sections:
                    prompt += " Organizza in paragrafi con titoletti esplicativi."
                
                prompt += " Mantieni tutto il contenuto, rimuovi elementi del parlato.\nTesto:\n" + chunk
                
                # Esegui riformulazione con timeout
                start_time = time.time()
                output = reformulator(
                    prompt, 
                    max_new_tokens=512,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9
                )
                
                # Estrai il testo generato
                generated_text = output[0]['generated_text'].strip()
                
                # Valida output
                if not generated_text or len(generated_text) < 20:
                    logger.warning(f"Output troppo corto per chunk {i+1}")
                    generated_text = f"[Chunk {i+1}: Output non valido]"
                
                # Verifica timeout
                if time.time() - start_time > 60:  # 60 secondi timeout
                    logger.warning(f"Timeout per chunk {i+1}")
                    generated_text = f"[Chunk {i+1}: Timeout]"
                
                notes_by_block.append((chunk, generated_text))
                final_notes.append(generated_text)
                
            except Exception as e:
                logger.error(f"Errore riformulazione chunk {i+1}: {e}")
                error_text = f"[Chunk {i+1}: Errore di elaborazione]"
                notes_by_block.append((chunk, error_text))
                final_notes.append(error_text)
        
        # Combina risultati
        final_text = "\n\n".join(final_notes)
        
        # Verifica risultato finale
        if not final_text or len(final_text.strip()) < 50:
            logger.warning("Risultato finale troppo corto")
            return "", notes_by_block
        
        return final_text, notes_by_block
        
    except Exception as e:
        logger.error(f"Errore generale riformulazione: {e}")
        return "", []

def validate_reformulation_input(text, formal_level, use_sections):
    """Valida i parametri di input per la riformulazione"""
    errors = []
    
    if not text or not isinstance(text, str):
        errors.append("Testo non valido")
    
    if len(text.strip()) < 10:
        errors.append("Testo troppo corto")
    
    valid_levels = ["Medio", "Alto", "Molto Alto"]
    if formal_level not in valid_levels:
        errors.append(f"Livello formalità non valido: {formal_level}")
    
    if not isinstance(use_sections, bool):
        errors.append("Parametro use_sections deve essere booleano")
    
    return errors
