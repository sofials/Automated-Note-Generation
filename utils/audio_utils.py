import os
import time
import wave
import subprocess
from pydub import AudioSegment

def get_audio_duration_wav(path):
    with wave.open(path, "rb") as audio:
        frames = audio.getnframes()
        rate = audio.getframerate()
        duration = frames / float(rate)
        return duration  # secondi

def extract_audio(video_path, audio_path):
    try:
        if os.path.exists(audio_path):
            os.remove(audio_path)

        start = time.time()
        subprocess.run([
            'ffmpeg', '-y', '-i', video_path,
            '-vn', '-acodec', 'pcm_s16le', audio_path
        ], check=True)
        end = time.time()
        return True, end - start

    except Exception as e:
        print(f"❌ Errore FFmpeg: {e}")
        return False, 0

def split_audio(audio_path, chunk_duration=30):
    try:
        audio = AudioSegment.from_wav(audio_path)
        ms_per_chunk = chunk_duration * 1000
        chunks = [audio[i:i + ms_per_chunk] for i in range(0, len(audio), ms_per_chunk)]

        chunk_paths = []
        for i, chunk in enumerate(chunks):
            path = f"chunk_{i:02d}.wav"
            chunk.export(path, format="wav")
            chunk_paths.append(path)

        return chunk_paths

    except Exception as e:
        print(f"❌ Errore split audio: {e}")
        return []
