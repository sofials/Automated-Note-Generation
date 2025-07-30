import streamlit as st
from utils.whisper_utils import transcribe_whisper_blocks
from utils.reformulate_utils import reformulate_transcription
from utils.audio_utils import load_audio_file, extract_audio
from utils.pdf_utils import save_pdf
import os
import sys

sys.path.append(os.path.abspath("."))

st.set_page_config(page_title="🧠 Appunti Universitari", layout="wide")
st.title("📚 Trascrizione & Appunti Universitari")

uploaded_file = st.file_uploader("🎙️ Carica file audio o video", type=["mp3", "wav", "m4a", "mp4"])
formal_level = st.selectbox("🎓 Livello di formalità", ["Medio", "Alto", "Molto Alto"])
add_sections = st.checkbox("🧩 Organizza in sottosezioni con titoletti")
compare_blocks = st.checkbox("🔍 Mostra confronto: parlato vs appunti")
generate_notes = st.checkbox("✏️ Riformula trascrizione in appunti scritti")

model_size = st.selectbox("🧠 Modello Whisper", ["tiny", "base", "small", "medium", "large"], index=3)
chunk_duration = st.slider("⏱️ Durata blocchi audio (sec)", min_value=10, max_value=120, value=30, step=10)

if uploaded_file:
    st.audio(uploaded_file)
    file_name = uploaded_file.name
    extension = file_name.split(".")[-1].lower()
    temp_input_path = f"temp_input.{extension}"

    with open(temp_input_path, "wb") as f:
        f.write(uploaded_file.read())

    if extension == "mp4":
        temp_audio_path = "temp_audio.wav"
        success, _ = extract_audio(temp_input_path, temp_audio_path)
        if not success:
            st.error("❌ Impossibile estrarre audio dal video.")
            st.stop()
    else:
        temp_audio_path = load_audio_file(open(temp_input_path, "rb"))

    progress_bar = st.progress(0)

    def update_progress(pct):
        progress_bar.progress(pct)

    with st.spinner("🎧 Trascrizione in corso..."):
        transcription, _ = transcribe_whisper_blocks(
            temp_audio_path,
            model_size=model_size,
            chunk_duration=chunk_duration,
            progress_callback=update_progress
        )

    st.text_area("📃 Trascrizione (grezza)", transcription, height=300)

    if generate_notes and transcription:
        with st.spinner("✍️ Generazione appunti..."):
            final_notes, notes_by_block = reformulate_transcription(
                transcription,
                formal_level=formal_level,
                use_sections=add_sections
            )

        if final_notes.strip() == "" or all(len(n.strip()) < 50 for n in final_notes.split("\n\n")):
            st.error("⚠️ Nessun appunto valido generato. Prova a ridurre la lunghezza dei blocchi o cambiare tono.")
        else:
            st.success("✅ Appunti generati!")
            st.text_area("📘 Appunti finali", final_notes, height=500)

            if compare_blocks:
                st.subheader("🔍 Confronto blocchi")
                for idx, (original, rewritten) in enumerate(notes_by_block):
                    st.markdown(f"**🎙️ Blocco {idx+1} - Originale**")
                    st.markdown(f"`{original.strip()}`")
                    st.markdown(f"**✏️ Riformulato**\n{rewritten.strip()}")
                    st.divider()

            st.download_button("💾 Scarica Appunti .txt", final_notes, file_name="appunti.txt")

            pdf_filename_notes = "appunti_riformulati.pdf"
            save_pdf(final_notes, title="Appunti Universitari", filename=pdf_filename_notes)
            with open(pdf_filename_notes, "rb") as file:
                st.download_button("📘 Scarica PDF Appunti", file, file_name=pdf_filename_notes, mime="application/pdf")
    else:
        st.info("ℹ️ Appunti non riformulati. Scarica solo la trascrizione.")

    pdf_filename_transcription = "trascrizione.pdf"
    save_pdf(transcription, title="Trascrizione Lezione", filename=pdf_filename_transcription)
    with open(pdf_filename_transcription, "rb") as file:
        st.download_button("📄 Scarica PDF Trascrizione", file, file_name=pdf_filename_transcription, mime="application/pdf")

    # 🧹 Cleanup
    if os.path.exists(temp_audio_path):
        os.remove(temp_audio_path)
    if os.path.exists(temp_input_path):
        os.remove(temp_input_path)

else:
    st.info("☝️ Carica un file audio o video per iniziare")
