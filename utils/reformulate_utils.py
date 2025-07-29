# utils/reformulate_utils.py

from transformers import pipeline
import re

# Inizializza il modello
reformulator = pipeline("text2text-generation", model="google/flan-t5-large")

def clean_text(text):
    # Rimuove interiezioni, ripetizioni semplici, pause comuni
    text = re.sub(r'\b(ehm+|mmm+|tipo|cioè)\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'(\.\s*){2,}', '. ', text)
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()

def split_chunks(text, max_chars=2000):
    return [text[i:i + max_chars] for i in range(0, len(text), max_chars)]

def reformulate_transcription(text, formal_level="Medio", use_sections=False):
    # Pulizia + segmentazione
    cleaned = clean_text(text)
    chunks = split_chunks(cleaned)
    notes_by_block = []

    final_notes = []

    for chunk in chunks:
        prompt = f"Converti questo testo parlato in appunti scritti, tono {formal_level.lower()}."
        if use_sections:
            prompt += " Organizza in paragrafi tematici con titoli esplicativi."

        prompt += " Mantieni tutto il contenuto, rimuovi elementi del parlato.\nTesto:\n" + chunk

        output = reformulator(prompt)[0]['generated_text']
        notes_by_block.append((chunk, output))
        final_notes.append(output)

    return "\n\n".join(final_notes), notes_by_block
