# 🧠 Appunti Universitari - Trascrizione & Riformulazione

Un'applicazione Streamlit per trascrivere file audio/video e convertirli in appunti universitari strutturati utilizzando Whisper e modelli di linguaggio.

## ✨ Funzionalità

- 🎧 **Trascrizione automatica** con OpenAI Whisper
- ✏️ **Riformulazione intelligente** in appunti strutturati
- 🎬 **Supporto video** (estrazione audio automatica)
- 📄 **Esportazione multipla** (PDF, TXT)
- 🔍 **Confronto blocchi** (originale vs riformulato)
- ⚙️ **Configurazioni flessibili** (formalità, modelli, durata blocchi)

## 🚀 Installazione

### Prerequisiti

- Python 3.8+
- FFmpeg (per supporto video)

### Installazione FFmpeg

**Windows:**
```bash
# Con Chocolatey
choco install ffmpeg

# Con Scoop
scoop install ffmpeg

# Download manuale da https://ffmpeg.org/download.html
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

### Installazione Python

1. **Clona il repository:**
```bash
git clone https://github.com/tuousername/LessionToNotes.git
cd LessionToNotes
```

2. **Crea ambiente virtuale:**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. **Installa dipendenze:**
```bash
pip install -r requirements.txt
```

## 🎯 Utilizzo

### Avvio rapido
```bash
python run_app.py
```

### Avvio manuale
```bash
streamlit run app.py
```

### Pulizia file temporanei
```bash
python clean.py
```

## 📋 Configurazioni

### Modelli Whisper
- **tiny**: Veloce, meno accurato
- **base**: Bilanciato
- **small**: Buona accuratezza
- **medium**: Ottima accuratezza (default)
- **large**: Massima accuratezza, più lento

### Livelli di formalità
- **Medio**: Linguaggio equilibrato
- **Alto**: Linguaggio formale
- **Molto Alto**: Linguaggio molto formale

### Durata blocchi audio
- **10-120 secondi**: Più corti = più veloci, più lunghi = più accurati
- **Consigliato**: 30 secondi

## 🛠️ Struttura Progetto

```
LessionToNotes/
├── app.py                 # Applicazione principale
├── run_app.py            # Script di avvio
├── clean.py              # Script di pulizia
├── requirements.txt      # Dipendenze Python
├── utils/
│   ├── audio_utils.py    # Gestione audio/video
│   ├── whisper_utils.py  # Trascrizione Whisper
│   ├── reformulate_utils.py  # Riformulazione testo
│   └── pdf_utils.py      # Generazione PDF
└── README.md
```

## 🔧 Risoluzione Problemi

### Errore "FFmpeg non trovato"
```bash
# Verifica installazione
ffmpeg -version

# Se non installato, segui istruzioni sopra
```

### Errore "Modello non trovato"
```bash
# Reinstalla dipendenze
pip install --upgrade -r requirements.txt
```

### Errore memoria insufficiente
- Riduci dimensione modello Whisper
- Riduci durata blocchi audio
- Chiudi altre applicazioni

### File troppo grande
- Limite: 500MB
- Comprimi file audio/video
- Usa formati più efficienti (MP3, WAV)

## 📊 Formati Supportati

### Input
- **Audio**: MP3, WAV, M4A
- **Video**: MP4

### Output
- **Testo**: TXT
- **Documento**: PDF

## 🔒 Sicurezza

- ✅ Sanitizzazione nomi file
- ✅ Validazione input
- ✅ Gestione errori robusta
- ✅ Cleanup automatico file temporanei
- ✅ Timeout per operazioni lunghe

## 🤝 Contributi

1. Fork del progetto
2. Crea branch feature (`git checkout -b feature/AmazingFeature`)
3. Commit modifiche (`git commit -m 'Add AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Apri Pull Request

## 📄 Licenza

Distribuito sotto licenza MIT. Vedi `LICENSE` per maggiori informazioni.

## 🆘 Supporto

Per problemi o domande:
1. Controlla la sezione "Risoluzione Problemi"
2. Cerca issues esistenti
3. Crea una nuova issue con dettagli completi

## 🔄 Changelog

### v2.0.0
- ✅ Gestione errori robusta
- ✅ Validazioni complete
- ✅ Cleanup automatico
- ✅ UI migliorata
- ✅ Documentazione completa

### v1.0.0
- 🎧 Trascrizione base
- ✏️ Riformulazione semplice
- 📄 Esportazione PDF/TXT
