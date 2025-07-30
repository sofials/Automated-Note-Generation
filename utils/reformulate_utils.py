from transformers import pipeline
import re

reformulator = pipeline("text2text-generation", model="google/flan-t5-large")

def clean_text(text):
    text = re.sub(r'\b(ehm+|mmm+|tipo|cioè)\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'(\.\s*){2,}', '. ', text)
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()

def split_chunks(text, max_chars=1500):
    return [text[i:i + max_chars] for i in range(0, len(text), max_chars)]

def reformulate_transcription(text, formal_level="Medio", use_sections=False):
    cleaned = clean_text(text)
    chunks = split_chunks(cleaned)
    notes_by_block = []
    final_notes = []

    for chunk in chunks:
        prompt = (
            f"Converti il seguente testo parlato in appunti scritti, tono {formal_level.lower()}."
        )
        if use_sections:
            prompt += " Organizza in paragrafi con titoletti esplicativi."
        prompt += " Mantieni tutto il contenuto, rimuovi elementi del parlato.\nTesto:\n" + chunk

        try:
            output = reformulator(prompt, max_new_tokens=256)[0]['generated_text'].strip()
        except Exception:
            output = "❌ Errore nel modello per questo blocco."

        if output == "" or len(output) < 50:
            output = "⚠️ Nessun output valido per questo blocco."

        notes_by_block.append((chunk, output))
        final_notes.append(output)

    return "\n\n".join(final_notes), notes_by_block
