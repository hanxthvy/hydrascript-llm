#!/usr/bin/env python3
# [xihanzu-NR]
"""Dedup HYS dataset: hapus instruction duplikat, pertahankan entri pertama."""
import json
from pathlib import Path

JSONL = Path("/root/models/distilled_hys_1000/hydrascript_hys_dataset.jsonl")
TXT = Path("/root/models/distilled_hys_1000/hydrascript_hys_train.txt")

lines = JSONL.read_text(encoding="utf-8").splitlines()
seen = set()
unique = []
dupes = 0

for line in lines:
    if not line.strip():
        continue
    d = json.loads(line)
    key = d["instruction"]
    if key in seen:
        dupes += 1
        continue
    seen.add(key)
    unique.append(d)

print(f"Input : {len(lines)} baris")
print(f"Dupes : {dupes} dibuang")
print(f"Output: {len(unique)} unik")

JSONL.write_text("\n".join(json.dumps(d, ensure_ascii=False) for d in unique) + "\n", encoding="utf-8")
TXT.write_text("".join(d["formatted"] for d in unique), encoding="utf-8")

a = sum(1 for d in unique if d["teacher"] == "teacher_A")
b = sum(1 for d in unique if d["teacher"] == "teacher_B")
print(f"\nTeacher A: {a}")
print(f"Teacher B: {b}")
print(f"Ratio: {a/len(unique)*100:.1f}% : {b/len(unique)*100:.1f}%")
