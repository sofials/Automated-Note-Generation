import whisper
import time
import os
import tempfile
import shutil
from utils.audio_utils import split_audio, cleanup_temp_files, cleanup_temp_dirs

def transcribe_whisper_blocks(audio_path, language="it", model_size="medium", progress_callback=None, chunk_duration=30):
    """
    Trascrive audio usando Whisper con gestione errori robusta
    """
    temp_files = []
    temp_dirs = []
    
    try:
        # Validazione input
        if not os.path.exists(audio_path):
            raise ValueError(f"Percorso audio non valido: {audio_path}")
        
        if not os.path.getsize(audio_path) > 0:
            raise ValueError("File audio vuoto")
        
        # Validazione parametri
        valid_models = ["tiny", "base", "small", "medium", "large"]
        if model_size not in valid_models:
            raise ValueError(f"Modello non valido. Scegli tra: {valid_models}")
        
        if chunk_duration < 5 or chunk_duration > 300:
            raise ValueError("Durata chunk deve essere tra 5 e 300 secondi")
        
        # Carica modello con timeout
        try:
            model = whisper.load_model(model_size)
        except Exception as e:
            raise RuntimeError(f"Errore caricamento modello Whisper: {str(e)}")
        
        # Divide audio in chunks
        try:
            chunk_paths = split_audio(audio_path, chunk_duration)
            temp_files.extend(chunk_paths)
            
            # Ottieni directory temporanea per cleanup
            if chunk_paths:
                temp_dirs.append(os.path.dirname(chunk_paths[0]))
                
        except Exception as e:
            raise RuntimeError(f"Errore divisione audio: {str(e)}")
        
        if not chunk_paths:
            raise ValueError("Nessun chunk audio generato")
        
        # Trascrizione chunks
        all_texts = []
        total_chunks = len(chunk_paths)
        start_time = time.time()
        
        for i, chunk_path in enumerate(chunk_paths, start=1):
            try:
                # Verifica chunk prima della trascrizione
                if not os.path.exists(chunk_path) or os.path.getsize(chunk_path) == 0:
                    print(f"⚠️ Chunk {i} vuoto o mancante, saltato")
                    continue
                
                # Trascrizione con timeout
                result = model.transcribe(
                    chunk_path, 
                    language=language,
                    fp16=False  # Evita problemi di compatibilità
                )
                
                text = result.get("text", "").strip()
                if text:
                    all_texts.append(text)
                else:
                    print(f"⚠️ Chunk {i} senza testo trascritto")
                
                # Aggiorna progresso
                if progress_callback:
                    try:
                        progress_callback(i / total_chunks)
                    except Exception as e:
                        print(f"⚠️ Errore callback progresso: {e}")
                
            except Exception as e:
                print(f"❌ Errore trascrizione chunk {i}: {e}")
                # Continua con altri chunks invece di fallire completamente
                continue
        
        # Verifica risultati
        if not all_texts:
            raise RuntimeError("Nessun testo trascritto da nessun chunk")
        
        final_text = "\n\n".join(all_texts)
        
        # Verifica testo finale
        if len(final_text.strip()) < 10:
            raise RuntimeError("Trascrizione troppo corta, possibile errore")
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        return final_text, processing_time
        
    except Exception as e:
        print(f"❌ Errore Whisper: {e}")
        return "", 0
    
    finally:
        # Cleanup sicuro
        try:
            cleanup_temp_files(temp_files)
            cleanup_temp_dirs(temp_dirs)
        except Exception as e:
            print(f"⚠️ Errore cleanup: {e}")

def validate_whisper_model(model_size):
    """Valida se il modello Whisper è disponibile"""
    try:
        model = whisper.load_model(model_size)
        return True
    except Exception:
        return False

def get_available_whisper_models():
    """Restituisce lista modelli Whisper disponibili"""
    return ["tiny", "base", "small", "medium", "large"]
