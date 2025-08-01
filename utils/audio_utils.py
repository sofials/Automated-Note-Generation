import os
import time
import wave
import subprocess
import tempfile
import shutil
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError
try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False
    print("⚠️ soundfile non disponibile, usando validazione alternativa")

def validate_audio_file(audio_path):
    """Valida che il file audio sia valido e leggibile"""
    try:
        if not os.path.exists(audio_path):
            return False
        
        # Verifica dimensione file
        if os.path.getsize(audio_path) == 0:
            return False
        
        # Se soundfile è disponibile, usa per validazione avanzata
        if SOUNDFILE_AVAILABLE:
            try:
                with sf.SoundFile(audio_path) as f:
                    if f.frames == 0:
                        return False
                return True
            except Exception:
                return False
        else:
            # Validazione alternativa senza soundfile
            try:
                # Prova a leggere con pydub
                audio = AudioSegment.from_file(audio_path)
                if len(audio) == 0:
                    return False
                return True
            except Exception:
                return False
    except Exception:
        return False

def get_audio_duration_wav(path):
    """Ottiene durata file WAV con gestione errori"""
    try:
        with wave.open(path, "rb") as audio:
            frames = audio.getnframes()
            rate = audio.getframerate()
            return frames / float(rate)
    except Exception as e:
        print(f"❌ Errore lettura durata WAV: {e}")
        return 0

def check_ffmpeg_available():
    """Verifica se FFmpeg è disponibile"""
    try:
        result = subprocess.run(['ffmpeg', '-version'],
                                capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def extract_audio(video_path, audio_path):
    """Estrae audio da video con gestione errori robusta"""
    try:
        # Verifica FFmpeg
        if not check_ffmpeg_available():
            return False, "FFmpeg non trovato. Installa FFmpeg per supportare file video."
        # Verifica file input
        if not os.path.exists(video_path):
            return False, f"File video non trovato: {video_path}"
        # Rimuovi file output se esiste
        if os.path.exists(audio_path):
            os.remove(audio_path)
        # Esegui estrazione con timeout
        result = subprocess.run([
            'ffmpeg', '-y', '-i', video_path,
            '-vn', '-acodec', 'pcm_s16le', '-ar', '16000', audio_path
        ], capture_output=True, text=True, timeout=300, check=True)
        # Verifica file output
        if not os.path.exists(audio_path) or os.path.getsize(audio_path) == 0:
            return False, "Estrazione audio fallita - file output vuoto"
        return True, "Estrazione completata"
    except subprocess.TimeoutExpired:
        return False, "Timeout durante estrazione audio (5 minuti)"
    except subprocess.CalledProcessError as e:
        return False, f"Errore FFmpeg: {e.stderr}"
    except Exception as e:
        return False, f"Errore estrazione audio: {str(e)}"

def split_audio(audio_path, chunk_duration=30):
    """Divide audio in chunks con gestione errori"""
    temp_chunks = []
    try:
        # Verifica file audio
        if not validate_audio_file(audio_path):
            raise ValueError("File audio non valido")
        # Crea directory temporanea
        temp_dir = tempfile.mkdtemp(prefix="audio_chunks_")
        # Carica audio
        try:
            audio = AudioSegment.from_wav(audio_path)
        except CouldntDecodeError:
            # Prova altri formati
            audio = AudioSegment.from_file(audio_path)
        if len(audio) == 0:
            raise ValueError("File audio vuoto")
        # Converti in WAV se necessario
        if audio.frame_rate != 16000:
            audio = audio.set_frame_rate(16000)
        ms_per_chunk = chunk_duration * 1000
        chunks = [audio[i:i + ms_per_chunk] for i in range(0, len(audio), ms_per_chunk)]
        # Esporta chunks
        chunk_paths = []
        for i, chunk in enumerate(chunks):
            if len(chunk) == 0:
                continue
            path = os.path.join(temp_dir, f"chunk_{i:02d}.wav")
            chunk.export(path, format="wav", parameters=["-ar", "16000"])
            # Verifica chunk esportato
            if os.path.exists(path) and os.path.getsize(path) > 0:
                chunk_paths.append(path)
                temp_chunks.append(path)
        if not chunk_paths:
            raise ValueError("Nessun chunk valido generato")
        return chunk_paths
    except Exception as e:
        # Cleanup in caso di errore
        for chunk in temp_chunks:
            try:
                if os.path.exists(chunk):
                    os.remove(chunk)
            except:
                pass
        raise e

def load_audio_file(file_data, filename=None):
    """Carica file audio con gestione sicura"""
    try:
        # Crea directory temporanea sicura
        temp_dir = tempfile.mkdtemp(prefix="audio_temp_")
        if filename is None:
            filename = os.path.join(temp_dir, "temp_audio.wav")
        # Assicurati che sia un file WAV
        if not filename.endswith('.wav'):
            filename = os.path.splitext(filename)[0] + '.wav'
        # Scrivi file
        with open(filename, "wb") as f:
            f.write(file_data)
        # Valida file
        if not validate_audio_file(filename):
            raise ValueError("File audio non valido dopo scrittura")
        return filename
    except Exception as e:
        print(f"❌ Errore caricamento audio: {e}")
        raise

def cleanup_temp_files(file_paths):
    """Pulisce file temporanei in modo sicuro"""
    for path in file_paths:
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception as e:
            print(f"⚠️ Errore pulizia {path}: {e}")

def cleanup_temp_dirs(dir_paths):
    """Pulisce directory temporanee in modo sicuro"""
    for dir_path in dir_paths:
        try:
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
        except Exception as e:
            print(f"⚠️ Errore pulizia directory {dir_path}: {e}")