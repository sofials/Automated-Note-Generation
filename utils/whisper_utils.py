import whisper
import time
import streamlit as st
from utils.audio_utils import split_audio  # Usa la funzione che spezza l'audio in blocchi

def transcribe_whisper_blocks(audio_path, language="it", model_size="medium", progress_callback=None, chunk_duration=30):
    try:
        model = whisper.load_model(model_size)
        chunk_paths = split_audio(audio_path, chunk_duration)  # blocchi .wav

        all_texts = []
        total_chunks = len(chunk_paths)

        start_time = time.time()
        for i, chunk_path in enumerate(chunk_paths, start=1):
            result = model.transcribe(chunk_path, language=language)
            text = result["text"].strip()

            # 💾 Salva blocco singolo
            txt_path = chunk_path.replace(".wav", ".txt")
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(text)

            all_texts.append(text)

            if progress_callback:
                progress_callback(i / total_chunks)

        final_text = "\n\n".join(all_texts)

        # 💾 Salva file unico
        final_path = audio_path.replace(".wav", "_final.txt")
        with open(final_path, "w", encoding="utf-8") as f:
            f.write(final_text)

        end_time = time.time()
        return final_text, end_time - start_time

    except Exception as e:
        st.error(f"❌ Errore trascrizione blocchi Whisper: {e}")
        return "", 0
