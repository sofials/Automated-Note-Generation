import os
files = [f for f in os.listdir() if f.startswith("chunk_") or f.endswith(".wav") or f.endswith(".txt")]
for f in files:
    os.remove(f)
print("🧹 File temporanei eliminati")
