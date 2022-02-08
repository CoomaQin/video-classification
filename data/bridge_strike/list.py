import os
import random

split = 0.8
files = []
dataset = "train"
cls = ["negative", "positive"]
lbl = ["0", "1"]
for c, l in zip(cls, lbl):
    for r, d, f in os.walk(f"./{dataset}/{c}"):
        for n in f:
            files.append(f"./data/bridge_strike/{dataset}/{c}/{n} {l}")
        break
random.shuffle(files)
b = int(len(files) * split)
train = files[:b]
test = files[b:]
print("========================train=========================")
for item in train:
    print(item)
print("=========================test=========================")
for item in test:
    print(item)