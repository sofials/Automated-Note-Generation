import whisper
import time
import os
from utils.audio_utils import split_audio

def transcribe_whisper_blocks(audio_path, language="it", model_size="medium", progress_callback=None, chunk_duration=30):
    try:
        model = whisper.load_model(model_size)
        chunk_paths = split_audio(audio_path, chunk_duration)

        all_texts = []
        total_chunks = len(chunk_paths)
        start_time = time.time()

        for i, chunk_path in enumerate(chunk_paths, start=1):
            result = model.transcribe(chunk_path, language=language)
            text = result["text"].strip()

            all_texts.append(text)

            if progress_callback:
                progress_callback(i / total_chunks)

        final_text = "\n\n".join(all_texts)

        for path in chunk_paths:
            os.remove(path)

        end_time = time.time()
        return final_text, end_time - start_time

    except Exception as e:
        print(f"❌ Errore Whisper: {e}")
        return "", 0
