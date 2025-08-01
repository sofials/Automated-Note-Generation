import streamlit as st
from utils.whisper_utils import transcribe_whisper_blocks
from utils.reformulate_utils import reformulate_transcription, validate_reformulation_input
from utils.audio_utils import load_audio_file, extract_audio, validate_audio_file
from utils.pdf_utils import save_pdf, PDFGenerationError
import os
import sys
import tempfile
import shutil
import re
import logging
from pathlib import Path

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurazione pagina
st.set_page_config(
    page_title="🧠 Appunti Universitari", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Funzioni di utilità
def sanitize_filename(filename):
    """Sanitizza il nome del file per prevenire path injection"""
    if not filename:
        return None
    
    # Rimuovi caratteri pericolosi
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Limita lunghezza
    if len(sanitized) > 100:
        name, ext = os.path.splitext(sanitized)
        sanitized = name[:95] + ext
    return sanitized

def validate_file_size(file_size_mb, max_size_mb=500):
    """Valida dimensione file"""
    if file_size_mb > max_size_mb:
        st.error(f"❌ File troppo grande ({file_size_mb:.1f}MB). Massimo {max_size_mb}MB.")
        return False
    return True

def validate_file_type(extension):
    """Valida tipo file"""
    valid_extensions = ["mp3", "wav", "m4a", "mp4"]
    if extension.lower() not in valid_extensions:
        st.error(f"❌ Tipo file non supportato: {extension}")
        return False
    return True

# Interfaccia principale
st.title("📚 Trascrizione & Appunti Universitari")
st.markdown("---")

# Sidebar per configurazioni
with st.sidebar:
    st.header("⚙️ Configurazioni")
    
    formal_level = st.selectbox(
        "🎓 Livello di formalità", 
        ["Medio", "Alto", "Molto Alto"],
        help="Livello di formalità degli appunti generati"
    )
    
    add_sections = st.checkbox(
        "🧩 Organizza in sottosezioni", 
        help="Aggiunge titoletti esplicativi agli appunti"
    )
    
    compare_blocks = st.checkbox(
        "🔍 Mostra confronto blocchi", 
        help="Mostra confronto tra trascrizione originale e appunti"
    )
    
    generate_notes = st.checkbox(
        "✏️ Genera appunti scritti", 
        help="Riformula la trascrizione in appunti strutturati"
    )
    
    st.markdown("---")
    
    model_size = st.selectbox(
        "🧠 Modello Whisper", 
        ["tiny", "base", "small", "medium", "large"], 
        index=3,
        help="Modello Whisper per la trascrizione (più grande = più accurato)"
    )
    
    chunk_duration = st.slider(
        "⏱️ Durata blocchi audio (sec)", 
        min_value=10, 
        max_value=120, 
        value=30, 
        step=10,
        help="Durata di ogni blocco audio per la trascrizione"
    )

# Area principale
st.header("🎙️ Carica File Audio/Video")

uploaded_file = st.file_uploader(
    "Seleziona file audio o video", 
    type=["mp3", "wav", "m4a", "mp4"],
    help="Formati supportati: MP3, WAV, M4A, MP4 (massimo 500MB)"
)

# Variabili per cleanup
temp_files = []
temp_dirs = []

if uploaded_file:
    try:
        # Validazione file
        file_size_mb = uploaded_file.size / (1024 * 1024)
        if not validate_file_size(file_size_mb):
            st.stop()
        
        # Sanitizzazione nome file
        original_filename = uploaded_file.name
        sanitized_filename = sanitize_filename(original_filename)
        if not sanitized_filename:
            st.error("❌ Nome file non valido")
            st.stop()
        
        # Validazione estensione
        extension = sanitized_filename.split(".")[-1].lower()
        if not validate_file_type(extension):
            st.stop()
        
        # Mostra informazioni file
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📁 Nome file", sanitized_filename)
        with col2:
            st.metric("📏 Dimensione", f"{file_size_mb:.1f} MB")
        with col3:
            st.metric("🎵 Tipo", extension.upper())
        
        # Anteprima audio
        st.audio(uploaded_file)
        
        # Creazione file temporaneo sicuro
        try:
            # Crea directory temporanea sicura
            temp_dir = tempfile.mkdtemp(prefix="lesson_notes_")
            temp_dirs.append(temp_dir)
            
            temp_input_path = os.path.join(temp_dir, f"input.{extension}")
            temp_files.append(temp_input_path)
            
            # Salva file caricato
            with open(temp_input_path, "wb") as f:
                f.write(uploaded_file.read())
            
            # Gestione audio/video
            if extension == "mp4":
                temp_audio_path = os.path.join(temp_dir, "audio.wav")
                temp_files.append(temp_audio_path)
                
                with st.spinner("🎬 Estrazione audio dal video..."):
                    success, error_msg = extract_audio(temp_input_path, temp_audio_path)
                    if not success:
                        st.error(f"❌ Impossibile estrarre audio dal video: {error_msg}")
                        st.stop()
            else:
                # Per file audio diretti
                temp_audio_path = temp_input_path
            
            # Validazione file audio
            if not validate_audio_file(temp_audio_path):
                st.error("❌ File audio non valido o corrotto")
                st.stop()
            
            # Progress bar con gestione errori
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            def update_progress(pct, status="Trascrizione in corso..."):
                progress_bar.progress(pct)
                status_text.text(f"🎧 {status}")
            
            # Trascrizione con gestione errori
            st.header("🎧 Trascrizione")
            
            try:
                with st.spinner("🎧 Trascrizione in corso..."):
                    transcription, processing_time = transcribe_whisper_blocks(
                        temp_audio_path,
                        model_size=model_size,
                        chunk_duration=chunk_duration,
                        progress_callback=update_progress
                    )
                
                if not transcription or transcription.strip() == "":
                    st.error("❌ Trascrizione fallita. Verifica che il file contenga audio valido.")
                    st.stop()
                
                st.success(f"✅ Trascrizione completata in {processing_time:.1f}s")
                
                # Mostra trascrizione
                st.text_area(
                    "📃 Trascrizione (grezza)", 
                    transcription, 
                    height=300,
                    help="Trascrizione grezza del file audio"
                )
                
            except Exception as e:
                st.error(f"❌ Errore durante la trascrizione: {str(e)}")
                st.stop()
            
            # Generazione appunti
            if generate_notes and transcription:
                st.header("✏️ Generazione Appunti")
                
                try:
                    # Validazione input
                    validation_errors = validate_reformulation_input(transcription, formal_level, add_sections)
                    if validation_errors:
                        st.error(f"❌ Errori di validazione: {', '.join(validation_errors)}")
                        st.stop()
                    
                    with st.spinner("✍️ Generazione appunti..."):
                        final_notes, notes_by_block = reformulate_transcription(
                            transcription,
                            formal_level=formal_level,
                            use_sections=add_sections
                        )
                    
                    if not final_notes or final_notes.strip() == "":
                        st.warning("⚠️ Nessun appunto valido generato. Prova a ridurre la lunghezza dei blocchi o cambiare tono.")
                    else:
                        st.success("✅ Appunti generati!")
                        
                        # Mostra appunti
                        st.text_area(
                            "📘 Appunti finali", 
                            final_notes, 
                            height=500,
                            help="Appunti riformulati e strutturati"
                        )
                        
                        # Confronto blocchi
                        if compare_blocks and notes_by_block:
                            st.header("🔍 Confronto Blocchi")
                            
                            for idx, (original, rewritten) in enumerate(notes_by_block):
                                with st.expander(f"Blocco {idx+1}"):
                                    col1, col2 = st.columns(2)
                                    
                                    with col1:
                                        st.markdown("**🎙️ Originale**")
                                        st.markdown(f"`{original.strip()}`")
                                    
                                    with col2:
                                        st.markdown("**✏️ Riformulato**")
                                        st.markdown(rewritten.strip())
                        
                        # Download appunti
                        st.header("💾 Download")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.download_button(
                                "📄 Scarica Appunti .txt", 
                                final_notes, 
                                file_name="appunti.txt",
                                mime="text/plain",
                                help="Scarica appunti in formato testo"
                            )
                        
                        with col2:
                            try:
                                pdf_filename_notes = "appunti_riformulati.pdf"
                                save_pdf(final_notes, title="Appunti Universitari", filename=pdf_filename_notes)
                                with open(pdf_filename_notes, "rb") as file:
                                    st.download_button(
                                        "📘 Scarica PDF Appunti", 
                                        file, 
                                        file_name=pdf_filename_notes, 
                                        mime="application/pdf",
                                        help="Scarica appunti in formato PDF"
                                    )
                            except PDFGenerationError as e:
                                st.error(f"❌ Errore generazione PDF: {str(e)}")
                            except Exception as e:
                                st.error(f"❌ Errore generazione PDF: {str(e)}")
                
                except Exception as e:
                    st.error(f"❌ Errore generazione appunti: {str(e)}")
            else:
                st.info("ℹ️ Appunti non riformulati. Scarica solo la trascrizione.")
            
            # PDF trascrizione
            st.header("📄 Download Trascrizione")
            
            try:
                pdf_filename_transcription = "trascrizione.pdf"
                save_pdf(transcription, title="Trascrizione Lezione", filename=pdf_filename_transcription)
                with open(pdf_filename_transcription, "rb") as file:
                    st.download_button(
                        "📄 Scarica PDF Trascrizione", 
                        file, 
                        file_name=pdf_filename_transcription, 
                        mime="application/pdf",
                        help="Scarica trascrizione in formato PDF"
                    )
            except PDFGenerationError as e:
                st.error(f"❌ Errore generazione PDF trascrizione: {str(e)}")
            except Exception as e:
                st.error(f"❌ Errore generazione PDF trascrizione: {str(e)}")
        
        except Exception as e:
            st.error(f"❌ Errore generale: {str(e)}")
        
        finally:
            # Cleanup sicuro
            try:
                for temp_file in temp_files:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                
                for temp_dir in temp_dirs:
                    if os.path.exists(temp_dir):
                        shutil.rmtree(temp_dir)
            except Exception as e:
                st.warning(f"⚠️ Errore durante pulizia file temporanei: {str(e)}")
    
    except Exception as e:
        st.error(f"❌ Errore di validazione file: {str(e)}")

else:
    st.info("☝️ Carica un file audio o video per iniziare")
    
    # Informazioni utili
    st.markdown("---")
    st.markdown("""
    ### 📋 Informazioni
    
    **Formati supportati:**
    - 🎵 Audio: MP3, WAV, M4A
    - 🎬 Video: MP4
    
    **Limiti:**
    - 📏 Dimensione massima: 500MB
    - ⏱️ Durata consigliata: fino a 2 ore
    
    **Funzionalità:**
    - 🎧 Trascrizione automatica con Whisper
    - ✏️ Riformulazione in appunti strutturati
    - 📄 Esportazione in PDF e TXT
    """)