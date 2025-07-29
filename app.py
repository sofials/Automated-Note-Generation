import streamlit as st
import os
import textwrap
import time
from utils.audio_utils import extract_audio
from utils.whisper_utils import transcribe_whisper, get_audio_duration_wav

st.set_page_config(page_title="WhisperNotes", page_icon="🧠")
st.title("🎓 WhisperNotes – Appunti da Videolezioni")
st.markdown("Carica un video, scegli il modello Whisper e ottieni la trascrizione!")

# 📌 Sidebar: selezione modello
st.sidebar.title("⚙️ Impostazioni")
model_choice = st.sidebar.selectbox("Modello Whisper", ["tiny", "base", "medium", "large"])

def chunk_text(text, max_length=1000):
    return textwrap.wrap(text, max_length)

# 📥 Upload video
video_file = st.file_uploader("📽️ Carica video", type=["mp4", "mov", "avi"])
if video_file:
    video_path = "input_video.mp4"
    with st.spinner("💾 Salvataggio..."):
        with open(video_path, "wb") as f:
            f.write(video_file.read())

    audio_path = "temp_audio.wav"
    with st.spinner("🎧 Estrazione audio..."):
        success, audio_time = extract_audio(video_path, audio_path)

    if success:
        st.success(f"✅ Audio estratto in {audio_time:.2f} secondi")

        estimated_duration = get_audio_duration_wav(audio_path)
        timer_duration = int(estimated_duration * 0.8)

        progress = st.progress(0)
        status = st.empty()

        for i in range(timer_duration):
            time.sleep(1)
            percent = (i + 1) / timer_duration
            progress.progress(percent)
            status.text(f"⏳ Trascrizione in corso... {timer_duration - i - 1}s rimanenti")

        progress.empty()
        status.empty()

        # 🔊 Trascrizione con modello scelto
        transcription, trans_time = transcribe_whisper(audio_path, model_size=model_choice)

        if transcription:
            st.success(f"✅ Trascrizione completata in {trans_time:.2f} secondi")
            st.subheader("📝 Trascrizione")
            st.text_area("Testo completo", transcription, height=300)

            st.download_button("💾 Scarica la trascrizione", transcription, file_name="trascrizione.txt", mime="text/plain")
        else:
            st.error("❌ Errore nella trascrizione")
    else:
        st.error("❌ Errore nell’estrazione audio")
