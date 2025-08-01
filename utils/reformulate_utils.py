import requests
import json
import re
import time
import logging

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurazione Ollama
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "mistral:7b"

def check_ollama_available():
    """Verifica se Ollama è disponibile e il modello è caricato"""
    try:
        # Verifica se Ollama è in esecuzione
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code != 200:
            return False, "Ollama non risponde"
        
        # Verifica se il modello è disponibile
        models = response.json().get("models", [])
        model_names = [model["name"] for model in models]
        
        if OLLAMA_MODEL not in model_names:
            return False, f"Modello {OLLAMA_MODEL} non trovato. Esegui: ollama pull {OLLAMA_MODEL}"
        
        return True, "Ollama e modello disponibili"
        
    except requests.exceptions.ConnectionError:
        return False, "Ollama non in esecuzione. Avvia con: ollama serve"
    except Exception as e:
        return False, f"Errore verifica Ollama: {str(e)}"

def call_ollama(prompt, max_tokens=1000, temperature=0.7):
    """Chiama Ollama API per la generazione del testo"""
    try:
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "top_p": 0.9,
                "top_k": 40
            }
        }
        
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=120  # 2 minuti timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "").strip()
        else:
            logger.error(f"Errore API Ollama: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        logger.error("Timeout chiamata Ollama")
        return None
    except Exception as e:
        logger.error(f"Errore chiamata Ollama: {e}")
        return None

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
    Riformula la trascrizione in appunti scritti usando Ollama Mistral:7b
    """
    if not text or not isinstance(text, str):
        return "", []
    
    try:
        # Verifica Ollama
        ollama_available, error_msg = check_ollama_available()
        if not ollama_available:
            logger.error(f"Ollama non disponibile: {error_msg}")
            return "", []
        
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
        
        notes_by_block = []
        final_notes = []
        
        for i, chunk in enumerate(chunks):
            try:
                # Crea prompt per Mistral
                prompt = f"""<s>[INST] Converti questo testo parlato in appunti universitari formali (livello {formal_level.lower()}).

Istruzioni:
- Mantieni tutto il contenuto importante
- Rimuovi elementi del parlato (ehm, mmm, tipo, cioè)
- Organizza in paragrafi chiari e strutturati
{f"- Aggiungi titoletti esplicativi per ogni sezione" if use_sections else ""}
- Usa un linguaggio formale e accademico
- Mantieni la coerenza logica

Testo da convertire:
{chunk} [/INST]</s>"""
                
                # Esegui riformulazione con Ollama
                start_time = time.time()
                generated_text = call_ollama(prompt, max_tokens=800, temperature=0.7)
                
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
