import os
import shutil
import tempfile
import logging
from pathlib import Path

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def cleanup_temp_files():
    """Pulisce tutti i file temporanei in modo sicuro"""
    cleaned_files = 0
    cleaned_dirs = 0
    
    try:
        # File temporanei da rimuovere
        temp_patterns = [
            "temp_*.wav",
            "temp_*.mp3", 
            "temp_*.m4a",
            "temp_*.mp4",
            "chunk_*.wav",
            "*.txt",
            "appunti_*.pdf",
            "trascrizione.pdf"
        ]
        
        # Directory temporanee da rimuovere
        temp_dirs = [
            "temp_chunks",
            "temp",
            "audio_chunks_*",
            "audio_temp_*",
            "lesson_notes_*"
        ]
        
        # Pulisci file temporanei
        for pattern in temp_patterns:
            try:
                for file_path in Path(".").glob(pattern):
                    if file_path.is_file():
                        try:
                            file_path.unlink()
                            cleaned_files += 1
                            logger.info(f"Rimosso file: {file_path}")
                        except Exception as e:
                            logger.warning(f"Errore rimozione {file_path}: {e}")
            except Exception as e:
                logger.warning(f"Errore pattern {pattern}: {e}")
        
        # Pulisci directory temporanee
        for dir_pattern in temp_dirs:
            try:
                for dir_path in Path(".").glob(dir_pattern):
                    if dir_path.is_dir():
                        try:
                            shutil.rmtree(dir_path)
                            cleaned_dirs += 1
                            logger.info(f"Rimossa directory: {dir_path}")
                        except Exception as e:
                            logger.warning(f"Errore rimozione directory {dir_path}: {e}")
            except Exception as e:
                logger.warning(f"Errore pattern directory {dir_pattern}: {e}")
        
        # Pulisci anche dalla directory tempfile di sistema
        try:
            temp_dir = tempfile.gettempdir()
            for item in os.listdir(temp_dir):
                if item.startswith(("lesson_notes_", "audio_chunks_", "audio_temp_")):
                    item_path = os.path.join(temp_dir, item)
                    try:
                        if os.path.isfile(item_path):
                            os.remove(item_path)
                            cleaned_files += 1
                        elif os.path.isdir(item_path):
                            shutil.rmtree(item_path)
                            cleaned_dirs += 1
                    except Exception as e:
                        logger.warning(f"Errore pulizia tempfile {item_path}: {e}")
        except Exception as e:
            logger.warning(f"Errore pulizia directory tempfile: {e}")
        
        logger.info(f"🧹 Pulizia completata: {cleaned_files} file e {cleaned_dirs} directory rimossi")
        
    except Exception as e:
        logger.error(f"❌ Errore durante pulizia: {e}")

def check_disk_space():
    """Verifica spazio disco disponibile"""
    try:
        import shutil
        total, used, free = shutil.disk_usage(".")
        free_gb = free // (1024**3)
        logger.info(f"💾 Spazio disco disponibile: {free_gb} GB")
        return free_gb
    except Exception as e:
        logger.warning(f"Impossibile verificare spazio disco: {e}")
        return None

if __name__ == "__main__":
    print("🧹 Avvio pulizia file temporanei...")
    
    # Verifica spazio disco
    free_space = check_disk_space()
    if free_space is not None and free_space < 1:
        print(f"⚠️ Attenzione: spazio disco limitato ({free_space} GB)")
    
    # Esegui pulizia
    cleanup_temp_files()
    
    print("✅ Pulizia completata!")
