# [xihanzu-NR]
import subprocess
import json
import re
import tempfile
import os

TEST_PROMPTS = [
    ("Navbar", "buatkan navbar responsif dengan hydrascript tailwind"),
    ("Button", "implementasikan komponen Button dengan varian primary dan secondary di hydrascript"),
    ("LoginForm", "buatkan komponen form login lengkap dengan validasi email dan password"),
    ("Select", "bikin elemen select native html dengan opsi list dan event onchange"),
    ("Modal", "buat komponen Modal konfirmasi dengan tombol cancel dan confirm"),
    ("Card", "buat komponen Card profil pengguna dengan foto, nama, dan bio"),
    ("Table", "buat komponen tabel data dinamis dengan header dan rows dari props"),
    ("Accordion", "buatkan accordion dropdown menggunakan tag details dan summary"),
    ("LogicUtils", "buat modul logic .hys untuk fungsi validasi email dan format mata uang rupiah"),
    ("ToolCall", "jalankan perintah terminal npm run build untuk kompilasi"),
]

LLAMA_CLI = "/tmp/llama.cpp/build/bin/llama-cli"
MODEL = "/root/models/qwen3_hydra_gguf/qwen3-hydrascript-q8_0.gguf"
HYDRA_BIN = "/usr/local/bin/hydra"

env = os.environ.copy()
env["LD_LIBRARY_PATH"] = f"/tmp/llama.cpp/build/bin:{env.get('LD_LIBRARY_PATH', '')}"

print("=== EVALUASI GENERASI QWEN3-0.6B TERHADAP HYDRA COMPILER ===")
passed = 0
total_code = 0

for name, prompt in TEST_PROMPTS:
    cmd = [
        LLAMA_CLI,
        "-m", MODEL,
        "-p", f"### Instruction:\n{prompt}\n\n### Response:\n",
        "-n", "400",
        "-t", "2",
        "--temp", "0.1",
        "--no-warmup",
        "-st",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, env=env)
    output = res.stdout

    # Cek tool call
    if "<tool_call>" in output:
        m = re.search(r"<tool_call>\s*(\{.*?\})\s*</tool_call>", output, re.DOTALL)
        if m:
            try:
                tc = json.loads(m.group(1))
                print(f"[{name}] TOOL CALL VALID: {tc.get('name')} {tc.get('arguments')}")
            except Exception as e:
                print(f"[{name}] TOOL CALL JSON INVALID: {e}")
        else:
            print(f"[{name}] TOOL CALL MALFORMED")
        continue

    # Extract code
    total_code += 1
    code_match = re.search(r"```(?:hyx|hys|hydrascript)?\n(.*?)```", output, re.DOTALL)
    if code_match:
        code = code_match.group(1).strip()
    else:
        # Fallback to lines after Response
        parts = output.split("### Response:\n")
        code = parts[-1].strip() if len(parts) > 1 else output.strip()

    ext = ".hys" if "Logic" in name else ".hyx"
    with tempfile.NamedTemporaryFile("w", suffix=ext, delete=False) as f:
        f.write(code)
        f_path = f.name

    check_res = subprocess.run([HYDRA_BIN, "--check", f_path], capture_output=True, text=True)
    os.remove(f_path)

    if check_res.returncode == 0:
        passed += 1
        print(f"[{name}] COMPILER PASS (100% Valid)")
    else:
        err_msg = check_res.stderr.strip() or check_res.stdout.strip()
        print(f"[{name}] COMPILER FAIL: {err_msg[:120]}")

print("------------------------------------------------------------")
print(f"Hasil: {passed}/{total_code} ({passed/total_code*100:.1f}%) Kode Lolos Compiler Hydra")
