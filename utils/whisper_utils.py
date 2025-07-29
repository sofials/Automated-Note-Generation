import os
import wave
import time
import whisper
import torch

def get_audio_duration_wav(path):
    with wave.open(path, "rb") as audio:
        frames = audio.getnframes()
        rate = audio.getframerate()
        duration = frames / float(rate)
        return duration  # secondi

def transcribe_whisper(audio_path, language="it", model_size="medium"):
    """
    Trascrive un file audio con Whisper usando GPU se disponibile.
    Puoi scegliere il modello: tiny, base, medium, large
    """
    try:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = whisper.load_model(model_size, device=device)

        start = time.time()
        result = model.transcribe(audio_path, language=language)
        end = time.time()

        text = result["text"]

        txt_path = audio_path.replace(".wav", ".txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)

        return text, end - start

    except Exception as e:
        print(f"❌ Errore Whisper: {e}")
        return "", 0
