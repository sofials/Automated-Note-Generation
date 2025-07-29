import subprocess
import time
import os
import wave

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
