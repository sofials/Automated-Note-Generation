import os
import time
import wave
import subprocess
from pydub import AudioSegment

def get_audio_duration_wav(path):
    with wave.open(path, "rb") as audio:
        frames = audio.getnframes()
        rate = audio.getframerate()
        return frames / float(rate)

def extract_audio(video_path, audio_path):
    try:
        if os.path.exists(audio_path):
            os.remove(audio_path)

        subprocess.run([
            'ffmpeg', '-y', '-i', video_path,
            '-vn', '-acodec', 'pcm_s16le', audio_path
        ], check=True)

        return True, time.time()

    except Exception as e:
        print(f"❌ Errore FFmpeg: {e}")
        return False, 0

def split_audio(audio_path, chunk_duration=30):
    try:
        temp_dir = "temp_chunks"
        os.makedirs(temp_dir, exist_ok=True)

        audio = AudioSegment.from_wav(audio_path)
        ms_per_chunk = chunk_duration * 1000
        chunks = [audio[i:i + ms_per_chunk] for i in range(0, len(audio), ms_per_chunk)]

        chunk_paths = []
        for i, chunk in enumerate(chunks):
            path = os.path.join(temp_dir, f"chunk_{i:02d}.wav")
            chunk.export(path, format="wav")
            chunk_paths.append(path)

        return chunk_paths

    except Exception as e:
        print(f"❌ Errore split audio: {e}")
        return []

def load_audio_file(uploaded_file, filename="temp/temp_audio.wav"):
    os.makedirs("temp", exist_ok=True)
    with open(filename, "wb") as f:
        f.write(uploaded_file.read())
    return filename
