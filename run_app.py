import subprocess
import os

try:
    print("🚀 Avvio Streamlit...")
    subprocess.run(["streamlit", "run", "app.py"])
finally:
    print("🧹 Pulizia in corso...")
    os.system("python clean.py")
    print("✅ Tutto pulito!")
