#!/usr/bin/env bash
# [xihanzu-NR]
"""
HydraScript .hys Distillation Engine — 1,000 Tasks
High-Concurrency Distillation Pipeline: 100 Workers Teacher A + 50 Workers Teacher B
100% Verified against Rust compiler `hydra --check`
Zero Watermark Pollution
"""
import argparse
import concurrent.futures
import json
import os
import re
import subprocess
import tempfile
import threading
import time
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

GATEWAY_URL = "http://127.0.0.1:20128/v1/messages"
MODELS_API_URL = "http://127.0.0.1:20128/v1/models"
API_KEY = os.environ.get("ROUTER_API_KEY", "")
HYDRA_BIN = "/usr/local/bin/hydra"

HYDRA_HYS_DOCTRINE = """You are the Supreme Authority and Core Compiler Engineer of HydraScript (.hys).
HydraScript .hys is the Pythonic Server/Logic/Backend language that compiles to Node.js ES Modules (.mjs).

STRICT RULES & CONSTRAINTS:
1. TARGET IS .hys (PURE LOGIC & BACKEND):
   - ABSOLUTELY NO JSX, NO TSX, NO HTML TAGS (div, span, button, p, h1, input, etc.).
   - ABSOLUTELY NO 'component' KEYWORD.
   - ABSOLUTELY NO REACT HOOKS (useState, useEffect, useCallback, etc.).
   - Code must be PURE logic, utilities, backend functions, algorithms, data transformers, or services.

2. CODE FENCE MANDATE (CRITICAL):
   - You MUST wrap all code inside ```hys ... ```.
   - NEVER EVER output ```hyx or ```python or ```javascript or ```tsx.
   - The opening tag MUST be exactly: ```hys

3. ZERO WATERMARK:
   - DO NOT output any comments like "# [xihanzu-NR]" or watermarks!

4. SYNTAX TRAPS (FROM RUST COMPILER SOURCE):
   - IMPORT SYNTAX: ALWAYS Pythonic:
       from "node:fs/promises" import readFile, writeFile
       from "node:path" import join, resolve
       from "node:crypto" import createHash, randomBytes, randomUUID
       import fs from "node:fs"
     NEVER use JS syntax: import { a, b } from "module" (Compile error!).
   - EXPORT SYNTAX: Define function first, then export at the bottom:
       def my_function(param):
           return param * 2
       export my_function
       export default my_function
     NEVER write 'export def my_function()' (Compile error!).
   - NO Python 'raise' -> ALWAYS use 'throw Error("message")'.
   - NO Python 'is' or 'is not' -> ALWAYS use '== None' or '!= None'.
   - NO 'class' keyword -> ALWAYS use factory functions: 'def create_service():' returning a dict of functions.
   - NO JS arrow functions '=>' -> Use 'lambda x: x + 1' or named 'def'.
   - NO ternary '? :' -> Use Python inline 'x = a if cond else b'.
   - NO '&&', '||', '!' -> Use 'and', 'or', 'not'.
   - NO semicolons ';'.
   - Indentation: Exactly 4 spaces per indent level (NO tabs).
   - Functions: 'def func_name(arg1, arg2="default"):' or 'async def async_func(param):'.
   - Slicing & F-strings:
       items[1:5], items[:-1], f"User: {name}, total: {amount}"
   - Loops & Comprehensions:
       for item in items: ...
       while condition: ...
       [x * 2 for x in nums if x > 0]
   - Error Handling:
       try:
           ...
       except err:
           ...
       finally:
           ...

OUTPUT FORMAT (Bilingual):
[Singkat, 1-2 kalimat penjelasan teknis arsitektur logic dalam Bahasa Indonesia]

```hys
[Kode HydraScript .hys 100% valid dan lolos compiler hydra]
```"""

# 38 Kurikulum Segments (Total = 1,000 tasks)
CURRICULUM_DATA: List[Tuple[str, str, int, List[str]]] = [
    ("SEG-01", "HYS vs HYX Boundary", 50, [
        "hys_file_identity", "hys_target_backend", "hys_no_component", "hys_no_jsx", "hys_no_html_tags",
        "hys_algorithm_logic", "hys_business_logic", "hys_data_pipeline", "hys_cli_logic", "hys_service_boundary"
    ]),
    ("SEG-02", "HYS Basic Syntax", 35, [
        "hys_indentation_clean", "hys_literal_types", "hys_identifier_naming", "hys_statement_flow", "hys_block_statement"
    ]),
    ("SEG-03", "Variables & Assignment", 35, [
        "hys_var_assignment", "hys_multiple_assignment", "hys_computed_assignment", "hys_scope_shadowing", "hys_default_values"
    ]),
    ("SEG-04", "Primitive Types & Values", 25, [
        "hys_string_number_bool", "hys_null_handling", "hys_type_conversion", "hys_primitive_guard", "hys_primitive_validation"
    ]),
    ("SEG-05", "Operators & Expressions", 35, [
        "hys_math_operators", "hys_comparison_operators", "hys_logical_and_or_not", "hys_pythonic_ternary", "hys_chained_calls"
    ]),
    ("SEG-06", "Conditional Logic", 30, [
        "hys_if_elif_else", "hys_guard_clauses", "hys_compound_conditions", "hys_early_return", "hys_business_rules"
    ]),
    ("SEG-07", "Loops & Iteration", 30, [
        "hys_for_in_loop", "hys_while_loop", "hys_break_continue", "hys_loop_accumulator", "hys_nested_iteration"
    ]),
    ("SEG-08", "Functions", 50, [
        "hys_def_function", "hys_async_def", "hys_default_args", "hys_higher_order_func", "hys_factory_function",
        "hys_closure_function", "hys_pure_function", "hys_function_composition", "hys_error_throwing_func"
    ]),
    ("SEG-09", "Arrays & Collections", 35, [
        "hys_array_slice", "hys_array_map_filter", "hys_array_reduce", "hys_array_deduplicate", "hys_array_chunk_partition"
    ]),
    ("SEG-10", "Objects & Object Operations", 30, [
        "hys_object_literal", "hys_nested_object_lookup", "hys_object_merge", "hys_object_transform", "hys_object_serialization"
    ]),
    ("SEG-11", "Strings & Text Processing", 25, [
        "hys_string_split_join", "hys_string_slugify", "hys_string_regex_search", "hys_string_masking", "hys_string_normalize"
    ]),
    ("SEG-12", "F-Strings & Formatting", 15, [
        "hys_fstring_variables", "hys_fstring_expressions", "hys_fstring_url_path", "hys_fstring_currency_format"
    ]),
    ("SEG-13", "Slicing & Pythonic Syntax", 20, [
        "hys_slice_range", "hys_slice_negative_index", "hys_slice_pagination", "hys_slice_batching"
    ]),
    ("SEG-14", "Destructuring & Spread", 20, [
        "hys_array_destructuring", "hys_object_destructuring", "hys_object_spread_merge", "hys_rest_parameters"
    ]),
    ("SEG-15", "Type System", 35, [
        "hys_type_alias_dict", "hys_type_guards", "hys_nullable_checks", "hys_runtime_type_assertions"
    ]),
    ("SEG-16", "Async Programming", 45, [
        "hys_async_await", "hys_promise_all", "hys_async_retry_backoff", "hys_async_timeout", "hys_async_queue_worker",
        "hys_async_file_pipeline", "hys_async_http_fetch"
    ]),
    ("SEG-17", "Error Handling", 25, [
        "hys_try_except_finally", "hys_throw_error", "hys_custom_error_factory", "hys_error_propagation", "hys_fallback_recovery"
    ]),
    ("SEG-18", "Module System", 50, [
        "hys_pythonic_imports", "hys_named_exports", "hys_default_exports", "hys_node_builtin_imports", "hys_barrel_export"
    ]),
    ("SEG-19", "JavaScript Runtime & Builtins", 30, [
        "hys_math_builtins", "hys_date_now_parse", "hys_json_parse_stringify", "hys_map_set_collections"
    ]),
    ("SEG-20", "Node.js Filesystem", 40, [
        "hys_fs_read_write_file", "hys_fs_readdir_walk", "hys_fs_mkdir_recursive", "hys_fs_stat_exists", "hys_fs_stream_backup"
    ]),
    ("SEG-21", "Node.js Path", 20, [
        "hys_path_join_resolve", "hys_path_basename_dirname", "hys_path_normalize_extname", "hys_path_security_sanitization"
    ]),
    ("SEG-22", "Environment & Process", 20, [
        "hys_process_env_loader", "hys_env_type_casting", "hys_process_argv_parser", "hys_runtime_config_service"
    ]),
    ("SEG-23", "HTTP & API Logic", 40, [
        "hys_http_client_fetch", "hys_http_post_json", "hys_api_bearer_auth", "hys_api_pagination_collector", "hys_api_retry_wrapper"
    ]),
    ("SEG-24", "JSON & Serialization", 25, [
        "hys_safe_json_parse", "hys_json_file_storage", "hys_json_deep_merge", "hys_json_flatten_unflatten"
    ]),
    ("SEG-25", "Data Transformation & ETL", 35, [
        "hys_etl_csv_to_json", "hys_etl_data_normalization", "hys_etl_aggregation_pipeline", "hys_etl_deduplication_clean"
    ]),
    ("SEG-26", "Validation & Business Logic", 35, [
        "hys_validate_email_phone", "hys_validate_schema_dict", "hys_business_discount_calculator", "hys_state_machine_transition"
    ]),
    ("SEG-27", "Authentication & Security", 25, [
        "hys_jwt_token_validation", "hys_password_hash_crypto", "hys_role_permission_guard", "hys_input_sanitization"
    ]),
    ("SEG-28", "Logging & Debugging", 15, [
        "hys_structured_logger", "hys_timestamp_log_formatter", "hys_error_stack_tracer"
    ]),
    ("SEG-29", "TypeScript -> HYS Translation", 35, [
        "ts_to_hys_async_service", "ts_to_hys_data_mapper", "ts_to_hys_file_handler", "ts_to_hys_validator_util"
    ]),
    ("SEG-30", "Requirement -> HYS", 30, [
        "req_to_hys_cli_tool", "req_to_hys_cache_manager", "req_to_hys_rate_limiter", "req_to_hys_webhook_handler"
    ]),
    ("SEG-31", "Code Repair", 45, [
        "repair_remove_jsx_from_hys", "repair_fix_raise_to_throw", "repair_fix_arrow_func_to_def", "repair_fix_js_import_syntax", "repair_fix_is_none_syntax"
    ]),
    ("SEG-32", "HYS Anti-Patterns", 25, [
        "antipattern_eliminate_ui_in_hys", "antipattern_eliminate_class_keyword", "antipattern_eliminate_semicolons_tabs"
    ]),
    ("SEG-33", "HYS Refactoring", 25, [
        "refactor_extract_hys_functions", "refactor_flatten_nested_callbacks", "refactor_idiomatic_pythonic_hys"
    ]),
    ("SEG-34", "HYS FIM / Code Completion", 20, [
        "fim_hys_function_body", "fim_hys_async_pipeline", "fim_hys_error_handler", "fim_hys_module_export"
    ]),
    ("SEG-35", "Multi-Concept HYS", 30, [
        "multi_fs_plus_crypto_plus_json", "multi_http_plus_retry_plus_cache", "multi_auth_plus_jwt_plus_roles"
    ]),
    ("SEG-36", "Complete HYS Modules", 20, [
        "complete_cli_data_migrator", "complete_file_watcher_backup", "complete_api_microservice_adapter"
    ]),
    ("SEG-37", "HYS Output Format & Language Fence", 15, [
        "fence_guarantee_hys_not_hyx", "fence_strict_bilingual_explanation"
    ]),
    ("SEG-38", "HYS Semantic Classification", 15, [
        "classify_pure_backend_hys", "classify_utility_library_hys"
    ]),
]

DOMAINS = [
    "e-commerce checkout", "fintech payment gateway", "user authentication & RBAC", "log rotation & compression",
    "cloud storage S3 adapter", "API rate limiter & throttling", "database migration runner", "webhook event dispatcher",
    "CSV & Excel parser", "email template renderer", "JWT token generator & refresher", "system metrics collector",
    "cache manager Redis-compatible", "task scheduler & cron", "file upload sanitizer", "audit log recorder"
]

VARIATIONS_INDO = [
    "Tuliskan modul logika HydraScript murni (.hys) untuk",
    "Buatkan fungsi backend Pythonic HydraScript (.hys) untuk",
    "Implementasikan utilitas logic .hys tanpa UI/JSX untuk",
    "Rancang modul backend .hys yang efisien dan aman untuk",
    "Kembangkan script utilitas server (.hys) di HydraScript untuk",
]


def build_hys_task_pool(teacher_a: str = "teacher_A", teacher_b: str = "teacher_B") -> List[Dict[str, Any]]:
    """Membangun 1,000 tasks terstruktur dengan pembagian proporsional 2:1 ke teacher_a dan teacher_b."""
    tasks = []
    task_idx = 0

    for seg_id, seg_name, target_count, subtopics in CURRICULUM_DATA:
        for i in range(target_count):
            subtopic = subtopics[i % len(subtopics)]
            domain = DOMAINS[(task_idx + i) % len(DOMAINS)]
            prefix = VARIATIONS_INDO[(task_idx + i) % len(VARIATIONS_INDO)]

            instruction = f"{prefix} fitur `{subtopic}` pada domain `{domain}`. Pastikan menggunakan sintaks .hys murni tanpa tag JSX/UI, import Pythonic `from \"modul\" import item`, throw Error untuk eksepsi, dan export di akhir file."

            # Rasio persis 50:50 (500 Teacher A : 500 Teacher B)
            if task_idx % 2 == 0:
                assigned_model = teacher_a
            else:
                assigned_model = teacher_b

            tasks.append({
                "id": task_idx + 1,
                "segment": seg_id,
                "segment_name": seg_name,
                "subtopic": subtopic,
                "domain": domain,
                "instruction": instruction,
                "model": assigned_model,
            })
            task_idx += 1
            if len(tasks) >= 1000:
                break
        if len(tasks) >= 1000:
            break

    return tasks[:1000]


GLOBAL_MAX_TOKENS = 50000
GLOBAL_TIMEOUT = 1800

# HTTP Session Manager
class HTTPClientPool:
    def __init__(self, api_key: str, gateway_url: str):
        self.api_key = api_key
        self.gateway_url = gateway_url

    def post_messages(self, prompt: str, model: str, max_tokens: int = 50000, timeout: int = 1800) -> str:
        payload = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": 0.2,
            "system": HYDRA_HYS_DOCTRINE,
            "messages": [{"role": "user", "content": prompt}]
        }
        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.gateway_url,
            data=data_bytes,
            headers={
                "content-type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
            },
            method="POST"
        )
        try:
            full_text = []
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                for line in resp:
                    line_str = line.decode("utf-8").strip()
                    if line_str.startswith("data:"):
                        raw_json = line_str[5:].strip()
                        if not raw_json or raw_json == "[DONE]":
                            continue
                        try:
                            ev = json.loads(raw_json)
                            if ev.get("type") == "content_block_delta":
                                delta = ev.get("delta", {})
                                if "text" in delta:
                                    full_text.append(delta["text"])
                        except json.JSONDecodeError:
                            continue
            return "".join(full_text).strip()
        except Exception:
            return ""


http_client = HTTPClientPool(API_KEY, GATEWAY_URL)


def sanitize_and_fix_hys(code: str) -> str:
    """Otomatis membetulkan slip sintaks umum sebelum pengujian compiler."""
    # 1. Hapus watermark dan internal comments bila ada
    code = re.sub(r"#\s*\[xihanzu-NR\]", "", code)
    code = re.sub(r"//\s*\[xihanzu-NR\]", "", code)
    code = re.sub(r"#\s*ponytail:.*$", "", code, flags=re.MULTILINE)
    code = re.sub(r"#\s*\[.*?\]", "", code)

    # 2. Fix JS import: import { a, b } from "module" -> from "module" import a, b
    def _fix_import(m):
        items = m.group(1).strip()
        mod = m.group(2).strip()
        return f'from "{mod}" import {items}'
    code = re.sub(r'import\s*\{\s*([^}]+)\s*\}\s*from\s*["\']([^"\']+)["\']', _fix_import, code)

    # 3. Fix export def foo( -> def foo( ... export foo
    exported_names = []
    lines = []
    for line in code.split("\n"):
        m_exp = re.match(r"^export\s+(?:async\s+)?def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", line)
        if m_exp:
            name = m_exp.group(1)
            exported_names.append(name)
            line = re.sub(r"^export\s+", "", line)
        lines.append(line)
    code = "\n".join(lines)

    if exported_names and "export " not in code.split("\n")[-2:]:
        code = code.rstrip() + "\n\nexport " + ", ".join(exported_names) + "\n"

    # 4. Fix Python 'is not None' dan 'is None'
    code = re.sub(r"\bis not None\b", "!= None", code)
    code = re.sub(r"\bis None\b", "== None", code)

    # 5. Fix Python 'raise Error(' -> 'throw Error('
    code = re.sub(r"\braise\s+Error\(", "throw Error(", code)
    code = re.sub(r"\braise\s+Exception\(", "throw Error(", code)

    return code.strip()


def extract_hys_code_and_explanation(raw_text: str) -> Tuple[str, str]:
    """Ekstrak blok ```hys dan penjelasan bahasa Indonesia."""
    # Cari blok ```hys (atau fallback ```hyx yang akan kita konversi ke hys)
    match = re.search(r"```(?:hys|hyx|python)\s*([\s\S]*?)```", raw_text, re.IGNORECASE)
    if not match:
        return "", ""

    code = match.group(1).strip()
    code = sanitize_and_fix_hys(code)

    # Ambil penjelasan sebelum blok kode
    explanation_part = raw_text[:match.start()].strip()
    explanation_lines = [l for l in explanation_part.split("\n") if l.strip() and not l.strip().startswith("[Start thinking]") and not l.strip().startswith("```")]
    explanation = " ".join(explanation_lines).strip()
    if not explanation:
        explanation = "Modul logika backend HydraScript (.hys) fungsional murni tanpa komponen UI."

    return code, explanation


def verify_hys_compiler(code: str) -> bool:
    """Menguji kode langsung dengan compiler Rust hydra --check."""
    if not code:
        return False
    # Dilarang ada komponen UI
    if re.search(r"\bcomponent\s+[A-Za-z0-9_]+\s*\(", code):
        return False
    if re.search(r"\b(div|span|button|input|form)\s*\(", code):
        return False

    with tempfile.NamedTemporaryFile("w", suffix=".hys", delete=False) as f:
        f.write(code)
        f_path = f.name

    try:
        res = subprocess.run([HYDRA_BIN, "--check", f_path], capture_output=True, text=True, timeout=5)
        return res.returncode == 0
    except Exception:
        return False
    finally:
        if os.path.exists(f_path):
            os.remove(f_path)


# Progress Tracker
lock = threading.Lock()
dup_lock = threading.Lock()
dup_count = 0
active_workers_A = 0
active_workers_B = 0
completed_tasks = 0
total_tokens_est = 0


def process_task(task_item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    global active_workers_A, active_workers_B, completed_tasks, total_tokens_est
    model = task_item["model"]

    with lock:
        if model == "teacher_A":
            active_workers_A += 1
        else:
            active_workers_B += 1

    try:
        # Coba generate hingga 3 kali jika compiler gagal
        for attempt in range(3):
            prompt = task_item["instruction"]
            if attempt > 0:
                prompt += " PENTING: Jangan gunakan keyword 'component' atau tag UI. Pastikan sintaks Pythonic 'from \"modul\" import item' dan throw Error()."

            raw_response = http_client.post_messages(
                prompt,
                model=model,
                max_tokens=GLOBAL_MAX_TOKENS,
                timeout=GLOBAL_TIMEOUT
            )
            if not raw_response:
                continue

            code, explanation = extract_hys_code_and_explanation(raw_response)
            if not code:
                continue

            if verify_hys_compiler(code):
                formatted = (
                    f"### Instruction:\n{task_item['instruction']}\n\n"
                    f"### Response:\n{explanation}\n\n"
                    f"```hys\n{code}\n```\n<|endoftext|>\n"
                )
                return {
                    "type": "hys_logic",
                    "segment": task_item["segment"],
                    "subtopic": task_item["subtopic"],
                    "domain": task_item["domain"],
                    "teacher": model,
                    "instruction": task_item["instruction"],
                    "explanation": explanation,
                    "code": code,
                    "formatted": formatted
                }
        return None
    finally:
        with lock:
            if model == "teacher_A":
                active_workers_A -= 1
            else:
                active_workers_B -= 1


def run_parallel_hys_distillation(
    output_dir: str = "/root/models/distilled_hys_1000",
    teacher_a: str = "teacher_A",
    teacher_b: str = "teacher_B",
    workers_a: int = 100,
    workers_b: int = 50,
    max_tokens: int = 15000,
    timeout: int = 360,
):
    global completed_tasks, total_tokens_est, GLOBAL_MAX_TOKENS, GLOBAL_TIMEOUT
    GLOBAL_MAX_TOKENS = max_tokens
    GLOBAL_TIMEOUT = timeout
    os.makedirs(output_dir, exist_ok=True)
    jsonl_path = os.path.join(output_dir, "hydrascript_hys_dataset.jsonl")
    txt_path = os.path.join(output_dir, "hydrascript_hys_train.txt")

    tasks = build_hys_task_pool(teacher_a, teacher_b)
    total_needed = len(tasks)

    # Resume check: pakai SET instruction unik, bukan jumlah baris.
    # Dulu pakai line count → task yang sama di-re-run (duplikat 190+).
    done_instructions = set()
    if os.path.exists(jsonl_path):
        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    done_instructions.add(json.loads(line)["instruction"])
                except json.JSONDecodeError:
                    continue

    completed_tasks = len(done_instructions)
    remaining_tasks = [t for t in tasks if t["instruction"] not in done_instructions]

    print("=" * 70)
    print("  🚀 HYDRASCRIPT HYS DISTILLATION ENGINE (1,000 TASKS)")
    print(f"  Target: {total_needed:,} Sampel (.hys logic & backend murni)")
    print(f"  Workers Teacher A ({teacher_a}): {workers_a} Threads")
    print(f"  Workers Teacher B ({teacher_b}): {workers_b} Threads")
    print(f"  Total Concurrency: {workers_a + workers_b} Parallel Requests")
    print(f"  Resume Pos: {completed_tasks:,} / {total_needed:,} sampel sudah ada")
    print(f"  Sisa Task : {len(remaining_tasks):,} (A={sum(1 for t in remaining_tasks if t['model'] == teacher_a)}, B={sum(1 for t in remaining_tasks if t['model'] == teacher_b)})")
    print(f"  Compiler Verifier: {HYDRA_BIN} (--check)")
    print("=" * 70)

    if not remaining_tasks:
        print("✅ Seluruh 1,000 task sudah selesai!")
        return

    t0 = time.time()

    # Pisahkan task per pool
    tasks_A = [t for t in remaining_tasks if t["model"] == teacher_a]
    tasks_B = [t for t in remaining_tasks if t["model"] == teacher_b]

    with open(jsonl_path, "a", encoding="utf-8") as f_jsonl, open(txt_path, "a", encoding="utf-8") as f_txt:
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers_a, thread_name_prefix="pool_A") as pool_A, \
             concurrent.futures.ThreadPoolExecutor(max_workers=workers_b, thread_name_prefix="pool_B") as pool_B:

            future_to_task = {}

            queue_A = list(tasks_A)
            queue_B = list(tasks_B)

            # Submit initial batch to fill both pools completely
            for _ in range(min(workers_a, len(queue_A))):
                t = queue_A.pop(0)
                fut = pool_A.submit(process_task, t)
                future_to_task[fut] = (t, "A")

            for _ in range(min(workers_b, len(queue_B))):
                t = queue_B.pop(0)
                fut = pool_B.submit(process_task, t)
                future_to_task[fut] = (t, "B")

            while future_to_task and completed_tasks < total_needed:
                done, _ = concurrent.futures.wait(future_to_task.keys(), return_when=concurrent.futures.FIRST_COMPLETED)
                for fut in done:
                    task_item, pool_type = future_to_task.pop(fut)
                    try:
                        res = fut.result()
                    except Exception:
                        res = None

                    if res:
                        # Anti-duplikat: kalau instruksinya sudah tercatat, jangan tulis lagi.
                        global dup_count
                        with dup_lock:
                            is_dup = res["instruction"] in done_instructions
                            if not is_dup:
                                done_instructions.add(res["instruction"])
                            else:
                                dup_count += 1
                        if is_dup:
                            if pool_type == "A" and queue_A:
                                nxt = queue_A.pop(0)
                                future_to_task[pool_A.submit(process_task, nxt)] = (nxt, "A")
                            elif pool_type == "B" and queue_B:
                                nxt = queue_B.pop(0)
                                future_to_task[pool_B.submit(process_task, nxt)] = (nxt, "B")
                            continue

                        completed_tasks += 1
                        f_jsonl.write(json.dumps(res, ensure_ascii=False) + "\n")
                        f_jsonl.flush()
                        f_txt.write(res["formatted"])
                        f_txt.flush()

                        tok_est = len(res["formatted"]) // 4
                        total_tokens_est += tok_est
                        dt = time.time() - t0
                        speed = completed_tasks / max(1.0, dt)

                        print(
                            f"[{completed_tasks:4d}/{total_needed}] "
                            f"[In-Flight: A={active_workers_A:2d} B={active_workers_B:2d}] "
                            f"[{res['segment']:<6}] [{res['teacher']:<9}] "
                            f"Tokens: ~{total_tokens_est:,} | "
                            f"Speed: {speed:.1f} req/s | "
                            f"Elapsed: {dt/60:.1f}m",
                            flush=True
                        )
                    else:
                        # Masukkan kembali ke antrian untuk dicoba lagi
                        if pool_type == "A":
                            queue_A.append(task_item)
                        else:
                            queue_B.append(task_item)

                    # Langsung isi slot yang selesai dengan task berikutnya agar konkurensi selalu penuh
                    if pool_type == "A" and queue_A:
                        nxt = queue_A.pop(0)
                        new_fut = pool_A.submit(process_task, nxt)
                        future_to_task[new_fut] = (nxt, "A")
                    elif pool_type == "B" and queue_B:
                        nxt = queue_B.pop(0)
                        new_fut = pool_B.submit(process_task, nxt)
                        future_to_task[new_fut] = (nxt, "B")

    print("\n" + "=" * 70)
    print(f"  🎉 Distilasi 1,000 HYS Selesai Sempurna: {completed_tasks:,} / {total_needed:,}")
    print(f"  Dataset JSONL: {jsonl_path}")
    print(f"  Dataset TXT  : {txt_path}")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="HydraScript HYS Distillation (1,000 tasks)")
    parser.add_argument("--workers_a", type=int, default=50, help="Workers Teacher A (default: 50)")
    parser.add_argument("--workers_b", type=int, default=50, help="Workers Teacher B (default: 50)")
    parser.add_argument("--teacher_a", type=str, default="teacher_A", help="Combo Teacher A")
    parser.add_argument("--teacher_b", type=str, default="teacher_B", help="Combo Teacher B")
    parser.add_argument("--max_tokens", type=int, default=15000, help="Max output tokens (default: 15000)")
    parser.add_argument("--timeout", type=int, default=360, help="Timeout in seconds (default: 360)")
    parser.add_argument("--output_dir", type=str, default="/root/models/distilled_hys_1000", help="Output directory")

    args = parser.parse_args()
    run_parallel_hys_distillation(
        output_dir=args.output_dir,
        teacher_a=args.teacher_a,
        teacher_b=args.teacher_b,
        workers_a=args.workers_a,
        workers_b=args.workers_b,
        max_tokens=args.max_tokens,
        timeout=args.timeout,
    )


if __name__ == "__main__":
    main()
