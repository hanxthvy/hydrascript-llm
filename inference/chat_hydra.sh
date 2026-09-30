#!/usr/bin/env bash
# [xihanzu-NR]
export LD_LIBRARY_PATH="/tmp/llama.cpp/build/bin:${LD_LIBRARY_PATH:-}"
MODEL_PATH="/root/models/qn3_hxprjktv2_hydra/qn3-hxprjktv2-q8_0.gguf"
LLAMA_CLI="/tmp/llama.cpp/build/bin/llama-cli"

clear
echo "=================================================================="
echo "  ⚡ Qwen3-0.6B Fine-Tuned HydraScript V2 (qn3-hxprjktv2-q8_0)"
echo "  Dataset: 6,965 Samples (6K .hyx UI + 965 .hys Backend Logic)"
echo "  Format: GGUF Q8_0 (~610 MB) | Precision: High | Threads: 2 CPU"
echo "=================================================================="
echo ""

while true; do
    echo -e "\033[1;36mKetik prompt HydraScript (atau 'exit' untuk keluar):\033[0m"
    read -e -p "> " user_prompt
    if [[ -z "$user_prompt" ]]; then
        continue
    fi
    if [[ "$user_prompt" == "exit" || "$user_prompt" == "quit" ]]; then
        echo "Sampai jumpa!"
        break
    fi
    echo ""
    echo -e "\033[1;32m[Generating...]\033[0m"
    $LLAMA_CLI \
      -m "$MODEL_PATH" \
      -p "### Instruction:\n$user_prompt\n\n### Response:\n" \
      -n 512 \
      -t 2 \
      --temp 0.2 \
      --no-warmup \
      -st 2>/dev/null
    echo ""
    echo "------------------------------------------------------------------"
done
