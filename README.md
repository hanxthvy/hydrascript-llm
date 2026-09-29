# [xihanzu-NR]
<div align="center">

# ⚡ HydraScript LLM (`qn3-hxprjkt`)

**Specialized Code LLM fine-tuned for HydraScript — a Pythonic meta-framework compiling to React (`.hyx`) and Node.js (`.hys`)**

[![Base Model](https://img.shields.io/badge/Base-Qwen3--0.6B-blue.svg)](https://huggingface.co/Qwen/Qwen3-0.6B)
[![Quantization](https://img.shields.io/badge/Format-GGUF%20Q8__0-green.svg)](https://github.com/ggerganov/llama.cpp)
[![Dataset](https://img.shields.io/badge/Dataset-6%2C965%20samples-orange.svg)](#dataset)
[![Compiler Verified](https://img.shields.io/badge/Compiler%20Pass-100%25-brightgreen.svg)](#compiler-verification)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## 📌 Overview

**HydraScript LLM** is a fine-tuned causal language model engineered specifically for **HydraScript**, an emerging dual-target programming language:

- **`.hyx`**: Pythonic syntax compiling to React/JSX UI components
- **`.hys`**: Pythonic syntax compiling to Node.js ESM server logic

Standard coding LLMs (even large ones) consistently fail on HydraScript because of **strict compiler rules** that look like Python but have subtle, unforgiving syntax differences. This model was trained on **6,965 curated, compiler-verified samples** to produce syntactically valid HydraScript code with near-zero syntax errors.

---

## 🏗️ Architecture & Specs

| Property | Value |
|---|---|
| **Base Model** | `Qwen/Qwen3-0.6B` (606M parameters) |
| **Layers / Heads** | 28 layers, 16 Q heads / 8 KV heads (GQA) |
| **Hidden Size** | 1024 |
| **Context Window** | 1,024 tokens (expandable up to 32k) |
| **Fine-Tuning Method** | LoRA (rank=16, alpha=32, target=all-linear) |
| **Training Precision** | Native BF16 (No quantization during training) |
| **Target Hardware** | CPU-first (Intel/AMD with AVX-512) or any GPU |
| **Quantization** | Q8_0 GGUF (~610 MB) — near-lossless inference |
| **Inference Speed** | ~7–12 tok/s on a 4-core CPU VPS |

---

## 📊 Dataset Breakdown

The training dataset (V3 Combined) consists of **6,965 samples**:

```
Total: 6,965 samples (14.3 MB)
├── V2 UI Dataset (6,000 samples)
│   ├── Target: .hyx (React components, state, hooks, Tailwind)
│   ├── Format: Instruction → Code + Explanation
│   └── Distilled via: Teacher models with diverse prompt tasks
│
└── HYS Backend Dataset (965 samples)
    ├── Target: .hys (Pure backend logic, APIs, crypto, auth)
    ├── Curriculum: 38 structured segments (Basics → Advanced)
    ├── Teachers: 50% Teacher A (Atria) : 50% Teacher B (Space Bunny)
    ├── Max Tokens: 50,000 (deep reasoning before generation)
    └── Compiler Validation: 965/965 (100% PASS on `hydra --check`)
```

### 38-Segment HYS Curriculum

The backend logic dataset covers a comprehensive 38-segment curriculum:

<details>
<summary>Click to view all 38 curriculum segments</summary>

| Segment | Topic |
|---|---|
| SEG-01 | HYS vs HYX Boundary & Rules |
| SEG-02 | Pythonic Module Imports & Exports |
| SEG-03 | Async/Await & Event Loop |
| SEG-04 | Node.js Built-in Modules (fs, path, crypto) |
| SEG-05 | HTTP Servers & Middleware (Express/Fastify style) |
| SEG-06 | REST API Design & CRUD Patterns |
| SEG-07 | Database Integration (SQL/NoSQL) |
| SEG-08 | Authentication & JWT Patterns |
| SEG-09 | Validation & Serialization |
| SEG-10 | WebSocket & Real-time Communication |
| SEG-11 | Stream Processing & Buffers |
| SEG-12 | Process Management & Child Processes |
| SEG-13 | Worker Threads & Parallelism |
| SEG-14 | Logging & Observability |
| SEG-15 | Error Handling Patterns (`throw Error()`) |
| SEG-16 | Configuration & Environment Variables |
| SEG-17 | Caching Strategies (Redis, in-memory) |
| SEG-18 | Module System & Dynamic Imports |
| SEG-19 | Background Jobs & Queues |
| SEG-20 | File Upload & Multipart Handling |
| SEG-21 | Rate Limiting & Security Middlewares |
| SEG-22 | Testing & Assertion Patterns |
| SEG-23 | Utilities & Helper Functions |
| SEG-24 | Third-party API Clients |
| SEG-25 | CLI Tools & Argument Parsing |
| SEG-26 | Microservice Patterns |
| SEG-27 | Cryptography & Hashing |
| SEG-28 | Event Emitter Patterns |
| SEG-29 | Data Structures in HYS |
| SEG-30 | Functional Programming Patterns |
| SEG-31 | Design Patterns (Factory, Singleton, etc.) |
| SEG-32 | HYS Anti-Patterns & Common Traps |
| SEG-33 | HYS Refactoring Patterns |
| SEG-34 | HYS FIM / Code Completion |
| SEG-35 | Multi-Concept HYS Modules |
| SEG-36 | Complete HYS Application Modules |
| SEG-37 | Output Format & Language Fencing |
| SEG-38 | HYS Semantic Classification |

</details>

---

## ⚠️ HydraScript Syntax Rules (The 14 Traps)

The model was specifically aligned to follow the **HydraScript Compiler Rules** that trip up standard LLMs:

| ❌ Invalid (Compiler Error) | ✅ Valid HydraScript | Explanation |
|---|---|---|
| `import { hash } from "crypto"` | `from "crypto" import hash` | Pythonic import order, JS quoted string |
| `export def handler():` | `def handler():` ... `export handler` | Export at bottom, never inline |
| `const fn = () => {}` | `def fn():` or `lambda x: x * 2` | No JS arrow functions |
| `class UserService:` | `def create_user_service():` | No `class` keyword — use factory functions |
| `raise Error("fail")` | `throw Error("fail")` | JS `throw`, not Python `raise` |
| `if x is not None:` | `if x != None:` | No `is` / `is not` keywords |
| `if a && b:` | `if a and b:` | Python logical operators, not JS |
| `// comment` | `# comment` | Python-style `#` comments only |
| `x = cond ? a : b` | `x = a if cond else b` | Python ternary, not JS `? :` |
| Semicolons `;` | No semicolons | Strictly indentation-based |
| 2-space indentation | **4-space indentation** | Mandatory 4 spaces per indent level |

---

## 🚀 Quick Start

### 1. Requirements

- `llama.cpp` installed (or any GGUF-compatible runtime: Ollama, LM Studio, etc.)
- Model binary: `qn3-hxprjkt-q8_0.gguf` (~610 MB)

### 2. Run with `llama.cpp`

```bash
# Interactive CLI
llama-cli -m qn3-hxprjkt-q8_0.gguf \
  -c 1024 \
  --temp 0.2 \
  -p "### Instruction:\nTuliskan modul HYS untuk hash password dengan argon2\n\n### Response:\n"

# Or as OpenAI-compatible API server
llama-server -m qn3-hxprjkt-q8_0.gguf -c 2048 --port 8080
```

### 3. Prompt Format

The model uses the standard Alpaca instruction format:

```text
### Instruction:
{Your prompt here — describe the UI component (.hyx) or backend logic (.hys) you need}

### Response:
```

---

## 🛠️ Reproduction & Training

Training is fully reproducible via Kaggle (free Tesla T4 GPU, ~25 minutes):

```bash
# 1. Install dependencies
pip install -q -U transformers datasets peft accelerate

# 2. Run notebook
# Open training/kaggle_notebook_v3.ipynb on Kaggle
# Set Accelerator: GPU T4 x2 or GPU P100, Internet: On
```

### Key Training Hyperparameters

```python
per_device_train_batch_size = 1
gradient_accumulation_steps = 16  # Effective batch = 16
learning_rate = 2e-4
lr_scheduler_type = "cosine"
num_train_epochs = 3
max_seq_length = 1024
lora_r = 16
lora_alpha = 32
lora_target_modules = ["q_proj", "k_proj", "v_proj", "o_proj", 
                       "gate_proj", "up_proj", "down_proj"]
# Response-only loss masking: prompt tokens set to -100
```

---

## 📁 Repository Structure

```
hydrascript-llm/
├── README.md                     # This documentation
├── LICENSE                       # MIT License
├── .gitignore                    # Ignore large binaries, logs, datasets
│
├── distill/                      # Data distillation engine
│   ├── distill_hydra_v2.py       # V2 UI dataset distiller (6K samples)
│   ├── distill_hys_1000.py       # HYS backend logic distiller (38 segments)
│   └── fix_hys_dataset.py        # Dataset deduplication & verification
│
├── training/                     # Training & evaluation scripts
│   ├── kaggle_notebook_v3.ipynb  # End-to-end Kaggle training notebook
│   ├── auto_train_v2.py          # Legacy CPU training script (scratch model)
│   └── eval_hydra_compiler.py    # Automated Rust compiler validation
│
├── inference/                    # Deployment & serving scripts
│   ├── run.sh                    # Zellij / interactive chat launcher
│   ├── chat_hydra.sh             # llama-cli interactive loop
│   └── serve_files.py            # Local dataset HTTP server
│
├── datasets/                     # Dataset sample previews
│   └── sample_v3.jsonl           # 10 preview rows showing data format
│
└── docs/                         # Additional documentation
    └── TRAINING_REPORT.md        # Comprehensive evaluation report
```

---

## 🧪 Compiler Verification

Every sample generated during the HYS distillation pass was validated using the official Rust-based **`hydra --check`** compiler:

```bash
# Automated validation pipeline
python3 training/eval_hydra_compiler.py --dataset path/to/dataset.jsonl
```

- **Pass rate**: 100% (965 / 965 samples)
- **Watermark presence**: 0% (clean dataset)
- **Syntax violations detected**: 0

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

Base model [Qwen/Qwen3-0.6B](https://huggingface.co/Qwen/Qwen3-0.6B) is licensed under Apache 2.0.

---

<div align="center">
Built with ⚡ by <b>Hanxthvy</b>
</div>
