import os
files = []
for r, d, f in os.walk("./train/positive"):
    files.extend(f)
    break
print(files)
for f in files:
    print(f"./data/bridge_strike/train/positive/{f} 1")