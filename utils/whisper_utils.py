import time
import torch
from faster_whisper import WhisperModel
from utils.audio_utils import get_audio_duration_wav  # Assicurati che sia importato

def transcribe_whisper(audio_path, language="it", model_size="medium", progress_callback=None):
    try:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        compute_type = "float16" if device == "cuda" else "int8"

        model = WhisperModel(model_size, device=device, compute_type=compute_type)
        total_duration = get_audio_duration_wav(audio_path)

        start = time.time()
        segments_gen, info = model.transcribe(audio_path, language=language, beam_size=5)

        segments = []
        for seg in segments_gen:
            segments.append(seg)
            if progress_callback:
                percent = min(seg.end / total_duration, 1.0)
                progress_callback(percent)

        end = time.time()
        text = "\n".join([seg.text for seg in segments])

        txt_path = audio_path.replace(".wav", ".txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)

        return text, end - start

    except Exception as e:
        print(f"❌ Errore Faster-Whisper: {e}")
        return "", 0
