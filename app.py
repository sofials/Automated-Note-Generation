import streamlit as st
import os
from utils.audio_utils import extract_audio
from utils.whisper_utils import transcribe_whisper_blocks  # ← usa blocchi!

# 🧹 Pulizia controllata
for f in ["input_video.mp4", "temp_audio.wav"]:
    if os.path.exists(f):
        os.remove(f)

st.set_page_config(page_title="WhisperNotes", page_icon="🧠")
st.title("🎓 WhisperNotes – Appunti da Videolezioni")
st.markdown("Carica un video, scegli il modello Whisper e ottieni la trascrizione!")

# 🔧 Sidebar
st.sidebar.title("⚙️ Impostazioni")
model_choice = st.sidebar.selectbox("Modello Whisper", ["tiny", "base", "medium", "large"])
chunk_duration = st.sidebar.slider("Durata blocco (sec)", min_value=10, max_value=120, value=30)

# 📽️ Upload video
video_file = st.file_uploader("📽️ Carica video", type=["mp4", "mov", "avi"])
if video_file:
    video_path = "input_video.mp4"
    with st.spinner("💾 Salvataggio video..."):
        with open(video_path, "wb") as f:
            f.write(video_file.read())

    audio_path = "temp_audio.wav"
    with st.spinner("🎧 Estrazione audio..."):
        success, audio_time = extract_audio(video_path, audio_path)

    if success:
        st.success(f"✅ Audio estratto in {audio_time:.2f} secondi")
        progress = st.progress(0)
        status = st.empty()

        def update_progress(p):
            percent = int(p * 100)
            progress.progress(p)
            status.text(f"⏳ Trascrizione in corso... {percent}% completata")

        # 🧠 Trascrizione a blocchi
        transcription, trans_time = transcribe_whisper_blocks(
            audio_path,
            model_size=model_choice,
            progress_callback=update_progress,
            chunk_duration=chunk_duration
        )

        progress.empty()
        status.empty()

        final_txt_path = audio_path.replace(".wav", "_final.txt")
        if os.path.exists(final_txt_path):
            try:
                with open(final_txt_path, "r", encoding="utf-8") as f:
                    full_text = f.read()
            except Exception as e:
                st.error(f"❌ Errore lettura file finale: {e}")
                full_text = ""

            if full_text.strip():
                st.success(f"✅ Trascrizione completata in {trans_time:.2f} secondi")
                st.text_area("📝 Trascrizione finale", full_text, height=300)
                st.download_button("💾 Scarica trascrizione completa", full_text, file_name="trascrizione_completa.txt", mime="text/plain")
            else:
                st.warning("⚠️ Il file finale è vuoto.")
        else:
            st.warning("⚠️ Nessun file finale trovato.")

    else:
        st.error("❌ Errore nell’estrazione dell’audio")

# 🔁 Recupero manuale di un file precedente
st.markdown("---")
st.subheader("📄 Recupero manuale del file trascritto")

manual_txt_path = "temp_audio.txt"
if os.path.exists(manual_txt_path):
    try:
        with open(manual_txt_path, "r", encoding="utf-8") as f:
            manual_text = f.read()
        if manual_text.strip():
            st.info(f"ℹ️ Trascrizione già presente: {len(manual_text.strip())} caratteri")
            st.text_area("📝 Trascrizione manuale", manual_text, height=300)
            st.download_button("💾 Scarica manualmente .txt", manual_text, file_name="trascrizione.txt", mime="text/plain")
        else:
            st.warning("⚠️ Il file manuale è vuoto.")
    except Exception as e:
        st.error(f"❌ Errore nella lettura manuale: {e}")
else:
    st.info("📂 Nessun file manuale trovato (`temp_audio.txt`)")
