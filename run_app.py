import subprocess
import os
import sys
import signal
import time
import logging
from pathlib import Path

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Verifica che tutte le dipendenze siano installate"""
    required_packages = [
        "streamlit",
        "whisper", 
        "transformers",
        "torch",
        "pydub",
        "fpdf"
    ]
    
    optional_packages = [
        "soundfile"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"❌ Pacchetti mancanti: {', '.join(missing_packages)}")
        logger.error("Installa con: pip install -r requirements.txt")
        return False
    
    # Verifica pacchetti opzionali
    missing_optional = []
    for package in optional_packages:
        try:
            __import__(package)
        except ImportError:
            missing_optional.append(package)
    
    if missing_optional:
        logger.warning(f"⚠️ Pacchetti opzionali mancanti: {', '.join(missing_optional)}")
        logger.info("L'applicazione funzionerà con funzionalità ridotte")
    
    logger.info("✅ Tutte le dipendenze sono installate")
    return True

def check_ffmpeg():
    """Verifica che FFmpeg sia disponibile"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            logger.info("✅ FFmpeg trovato")
            return True
        else:
            logger.warning("⚠️ FFmpeg non trovato - supporto video limitato")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        logger.warning("⚠️ FFmpeg non trovato - supporto video limitato")
        return False

def cleanup_on_exit():
    """Esegue pulizia al termine dell'applicazione"""
    try:
        logger.info("🧹 Pulizia in corso...")
        
        # Esegui script di pulizia
        cleanup_script = Path("clean.py")
        if cleanup_script.exists():
            try:
                result = subprocess.run([sys.executable, "clean.py"], 
                                      capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    logger.info("✅ Pulizia completata")
                else:
                    logger.warning(f"⚠️ Errore pulizia: {result.stderr}")
            except subprocess.TimeoutExpired:
                logger.warning("⚠️ Timeout durante pulizia")
            except Exception as e:
                logger.error(f"❌ Errore esecuzione pulizia: {e}")
        else:
            logger.warning("⚠️ Script pulizia non trovato")
            
    except Exception as e:
        logger.error(f"❌ Errore durante pulizia: {e}")

def signal_handler(signum, frame):
    """Gestisce segnali di interruzione"""
    logger.info(f"🛑 Ricevuto segnale {signum}, terminazione in corso...")
    cleanup_on_exit()
    sys.exit(0)

def main():
    """Funzione principale"""
    try:
        # Registra handler per segnali
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        logger.info("🚀 Avvio applicazione...")
        
        # Verifica dipendenze
        if not check_dependencies():
            logger.error("❌ Dipendenze mancanti. Installa requirements.txt")
            sys.exit(1)
        
        # Verifica FFmpeg
        check_ffmpeg()
        
        # Verifica file app.py
        app_file = Path("app.py")
        if not app_file.exists():
            logger.error("❌ File app.py non trovato")
            sys.exit(1)
        
        logger.info("🎯 Avvio Streamlit...")
        
        # Avvia Streamlit
        try:
            subprocess.run([
                "streamlit", "run", "app.py",
                "--server.port", "8501",
                "--server.address", "localhost",
                "--browser.gatherUsageStats", "false"
            ], check=True)
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Errore Streamlit: {e}")
            sys.exit(1)
        except KeyboardInterrupt:
            logger.info("🛑 Interruzione manuale")
        except Exception as e:
            logger.error(f"❌ Errore imprevisto: {e}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Errore inizializzazione: {e}")
        sys.exit(1)
    
    finally:
        # Pulizia finale
        cleanup_on_exit()
        logger.info("✅ Applicazione terminata")

if __name__ == "__main__":
    main()
