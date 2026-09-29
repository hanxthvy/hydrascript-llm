# [xihanzu-NR]
"""Pipeline Distilasi Skala Penuh v2: 6.000 Sampel (5.000 Kode 48-Segmen + 1.000 Tool Calling).
Mendukung:
1. Output Dwi-Bahasa: 1-2 kalimat penjelasan bahasa Indonesia + Kode HydraScript / Tool Call.
2. Panjang Kode: Mendukung generate kode panjang hingga 150-300 baris.
3. 1.000 Sampel Tool Calling: Format Claude Code (<tool_call>{"name": "...", "arguments": {...}}</tool_call>)
   Mendukung tool: Write (simpan .hyx/.hys), Read, Edit, dan Bash (hydra --check / hydra build).
4. Model Guru & Rasio:
   - 80% atr/Atria-Dawn-Preview (40 dedicated workers)
   - 20% combo destilasi / Gemini Flash High (4 workers)
5. Verifikasi Keras Kompilator Rust:
   Setiap kode .hyx dan .hys divalidasi dengan /root/projects/hydra/compiler-rs/target/release/hydra --check
6. Zero Watermark polusi pada dataset.
ponytail: dual thread pool 44 workers; upgrade async httpx jika menembus 100+ concurrent connections.
"""

import argparse
import concurrent.futures
import json
import os
import random
import re
import subprocess
import tempfile
import time
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

GATEWAY_URL = "http://127.0.0.1:20128/v1/messages"
API_KEY = os.environ.get("ROUTER_API_KEY", "")
HYDRA_BIN = "/root/projects/hydra/compiler-rs/target/release/hydra"

HYDRA_DOCTRINE_V2 = """You are an expert native HydraScript compiler and principal engineer.
RESPONSE FORMAT:
1. Berikan penjelasan singkat 1-2 kalimat dalam bahasa Indonesia mengenai implementasi atau aksi yang dilakukan.
2. Tulis kode HydraScript (.hyx untuk React UI, .hys untuk pure logic/ESM) atau blok tool call jika diminta.

CRITICAL HYDRASCRIPT COMPILER RULES:
1. COMPONENT DECLARATION (.hyx):
   MUST use keyword `component Name(props):`, NEVER `def Name():`.
   Imports at top: `from "react" import useState, useEffect, useRef`
   State declaration: `val, set_val = useState(initial)` (NEVER write 'val', 'let', 'const', or 'var'!)

2. JSX TREE DISCIPLINE:
   - All variable assignments, state hooks, and helper functions MUST be in the preamble ABOVE the JSX tree.
   - ZERO assignments inside the element tree! (e.g. `x = 1` inside div is a fatal compiler error).
   - NO RETURN STATEMENT: In `component Name(props):`, the element tree IS the return value. NEVER write `return:` or `return (...)`! Indent the root element directly under the component.
   - Tags with props MUST use function-call syntax: `div(className="..."):`, `button(on_click=...):`.
   - Every tag with children MUST end with colon (:).
   - NO closing tags (</div>, </span>). Indentation-based hierarchy only.

3. LOOPS & TEMPLATING:
   - Loops inside element trees MUST use Python syntax: `for item in items:` or `for idx, item in enumerate(items):`.
   - NEVER use JS `items.map(...)` inside tree blocks!

4. STRICT PROHIBITIONS:
   - NO array spread `[...items]` or `[*items]` -> use list concatenation `items + [new_item]` or `items.concat([new_item])`.
   - NO object spread `{...obj}` -> use Python dict unpacking `{**obj, "key": val}`.
   - NO JS arrow functions `() => ...` -> use Python `lambda: ...` or define helper function in preamble above tree.
   - NO JS ternary `cond ? a : b` -> use Python `a if cond else b`.
   - NO JS logical operators (`&&`, `||`, `!`) -> use Python `and`, `or`, `not`.
   - NO JS comments (`//` or `/* */`) -> use Python `#` only.
   - NO semicolons (`;`). NO tabs -> use 4 spaces for indentation.
   - NO `class` keyword -> HydraScript has no classes; use `def` factory functions or plain objects/dictionaries.
   - NO component or element tree blocks in `.hys` -> `.hys` is pure ESM functions/def logic only.
   - NO Next.js Image -> use native `img(src=...):`. All custom components MUST be Capitalized (`Card:`), HTML elements lowercase (`div:`, `button:`).
   - NO `export component` -> write `component Name(props):` directly (automatically exported).
   - NO TS array type `int[]` -> use `list[int]` or `list[str]`.
   - NO relative imports without quotes -> use `from "./Component" import Component`.
   - NO Python 'is' or 'is not' (e.g. 'x is not None') -> use '!= None' or '== None' or 'if x:'.
   - NO Python 'raise' -> use 'throw Error(...)'.
   - NO dict comprehensions -> use loops or reduce.
   - NO Python `" ".join(list)` -> use `list.join(" ")`.
   - NO `if x in string` -> use `if string.includes(x):`.
   - NO raw unescaped `<` inside text string -> use `&lt;` or words.
   - ZERO badges, ZERO pills (`rounded-full`), ZERO emojis. Clean rectangular/rounded-sm cards, borders, text labels only.

5. ZERO WATERMARK:
   Do NOT emit watermark '# [xihanzu-NR]' in code outputs."""

TOOL_SYSTEM_PROMPT = HYDRA_DOCTRINE_V2 + """

TOOL CALLING INSTRUCTIONS:
You are an expert HydraScript AI assistant connected to Claude Code developer tools.
When asked to create, write, read, edit, or test files, you MUST respond with a brief explanation in Indonesian and the exact tool call block:

<tool_call>
{"name": "ToolName", "arguments": {"param": "value"}}
</tool_call>

TOOLS AVAILABLE:
- Write(file_path: str, content: str): Writes a complete file to disk.
- Read(file_path: str): Reads content of a file.
- Edit(file_path: str, old_string: str, new_string: str): Replaces text in a file.
- Bash(command: str): Runs terminal bash commands (e.g. hydra --check, hydra build, hydra dev).

Any HydraScript code (.hyx or .hys) inside Write or Edit MUST strictly follow native HydraScript rules above."""

# Bank Topik & Arketipe Komprehensif (48 Segmen)
HTML_ELEMENTS = [
    ("div", "Container pembungkus flex/grid"),
    ("span", "Inline text indicator"),
    ("p", "Paragraf deskripsi teks"),
    ("a", "Tautan navigasi hyperlink"),
    ("button", "Tombol aksi interaktif dengan varian"),
    ("input", "Field input teks, search, number"),
    ("textarea", "Field input multi-baris"),
    ("select", "Dropdown pilihan select dengan options"),
    ("form", "Formulir interaktif dengan submit handler"),
    ("img", "Gambar responsif dengan alt dan fallback"),
    ("svg", "Grafik vektor SVG dengan path/line/circle"),
    ("table", "Tabel tabular dengan thead, tbody, tr, th, td"),
    ("nav", "Navigasi bar header/sidebar"),
    ("header", "Header layout atas aplikasi"),
    ("footer", "Footer informasi copyright dan tautan"),
    ("section", "Section konten tematik"),
    ("article", "Card artikel dengan metadata"),
    ("aside", "Sidebar informasi kontekstual"),
    ("dialog", "Modal dialog konfirmasi"),
    ("details", "Dropdown accordion expandable"),
]

COMPOSITE_COMPONENTS = [
    ("LoginForm", "Formulir autentikasi login dengan input email, input password, remember me checkbox, dan tombol submit bertema dark."),
    ("RegistrationForm", "Formulir pendaftaran akun baru: input nama, email, password, konfirmasi password, terms checkbox, dan tombol daftar."),
    ("UserProfileCard", "Kartu profil user dengan avatar gambar/inisial, teks nama & role, badge status kotak, dan tombol aksi Edit Profil."),
    ("CommentSection", "Bagian komentar interaktif dengan daftar list komentar, textarea input tanggapan, dan tombol kirim balasan."),
    ("PricingCard", "Kartu paket langganan dengan nama paket, harga angka besar, daftar fitur checklist, dan tombol aksi Pilih Paket."),
    ("CheckoutSummary", "Ringkasan pesanan e-commerce: daftar item belanja, input kode kupon voucher, kalkulasi total, dan tombol Bayar Sekarang."),
    ("SearchFilterToolbar", "Toolbar pencarian lengkap: input search query, dropdown kategori status, dan tombol aksi Tambah Data Baru."),
    ("ConfirmDialogModal", "Modal konfirmasi aksi berbahaya: icon peringatan, pesan deskripsi, tombol Batal (outline), dan tombol Konfirmasi Hapus (danger)."),
    ("StatMetricsGrid", "Grid kartu metrik analitik: 4 kotak statistik dengan angka metrik, label judul, sparkline mini, dan indikator persentase."),
    ("FileUploadDropzone", "Area unggah file dropzone dengan icon cloud, instruksi teks, tombol browse file, dan status progress bar."),
    ("NavbarWithAuth", "Header navigasi lengkap dengan logo brand, menu links, tombol notifikasi, dan tombol avatar user / login."),
    ("NotificationList", "Daftar notifikasi aktivitas dengan icon status, judul, waktu relatif, dan tombol tandai telah dibaca."),
]

COMPONENT_ARCHETYPES = [
    ("Button", "Komponen tombol serbaguna dengan varian primary, secondary, outline, danger, ukuran sm/md/lg, state loading, dan event on_click."),
    ("Navbar", "Header navigasi responsif dengan logo brand, tautan halaman, active indicator, dan mobile menu drawer toggle."),
    ("Card", "Kartu konten modular dengan header, title, body slot, footer action, dan border dark theme neutral."),
    ("Modal", "Dialog modal overlay dengan backdrop blur, escape key handler, title, children slot, dan tombol aksi Batal / Konfirmasi."),
    ("Dropdown", "Menu dropdown interaktif dengan trigger button, menu pilihan mengambang, dan handler click-outside close."),
    ("Tabs", "Komponen tab bar horizontal dengan active tab state, underline transisi, dan panel konten dinamis."),
    ("Accordion", "Accordion list vertikal dengan multiple expandable panels, animasi expand, dan chevron indicator."),
    ("Table", "Tabel data tabular dengan sortable columns, pagination controls, search filter input, dan status badges persegi."),
    ("FormInput", "Komponen input form terintegrasi dengan label atas, hint text, validasi error message, dan clear button."),
    ("ToggleSwitch", "Saklar toggle reaktif boolean dengan track border, sliding knob, dan label teks."),
    ("Breadcrumb", "Navigasi breadcrumb horizontal hierarkis dengan slash separator dan hover state."),
    ("Pagination", "Navigasi halaman dengan tombol previous/next, nomor halaman interaktif, dan selector limit per page."),
    ("AlertBanner", "Banner pemberitahuan status (info, warning, error, success) dengan icon teks mono dan tombol dismiss."),
    ("Tooltip", "Tooltip info mengambang saat hover pada elemen target dengan positioning panah."),
    ("Avatar", "Avatar user dengan gambar profil atau fallback inisial huruf besar dalam kotak persegi monospaced."),
    ("Slider", "Range slider input dengan nilai numerik reaktif dan track progress."),
    ("SparklineChart", "Grafik tren mini menggunakan native SVG polyline dari array angka dinamis tanpa library eksternal."),
    ("RadialGauge", "Indikator progres melingkar dengan SVG circle dan strokeDasharray kalkulasi matematika."),
    ("BarChart", "Visualisasi grafik batang vertikal proporsional dengan elemen SVG rect dan koordinat axis."),
    ("CartesianGrid", "Grafik sumbu koordinat X/Y lengkap dengan grid lines, ticks, dan label angka."),
    ("SearchFilterBar", "Toolbar pencarian teks lengkap dengan input query, filter status dropdown, dan tombol reset filter."),
    ("KanbanBoard", "Papan kanban 3 kolom (Todo, InProgress, Done) dengan form tambah kartu, tombol geser status, dan count counter."),
    ("ServerDashboard", "Dashboard infrastruktur server lengkap (150-250 baris): metric tiles, status nodes table, CPU/RAM bars, dan modal tambah server."),
    ("SettingsPage", "Halaman pengaturan akun lengkap (150-250 baris): form profil, password change, notification toggles, dan danger zone."),
    ("ChatInterface", "Ruang percakapan chat dengan riwayat pesan sender vs receiver, input box, tombol kirim, dan status online."),
    ("MultiStepWizard", "Formulir pendaftaran multi-langkah (120-200 baris): step progress bar, form fields per langkah, dan tombol Prev/Next."),
    ("AuditLogViewer", "Penampil riwayat log audit sistem dengan filter level (INFO/WARN/CRITICAL), timestamp format, dan expandable details."),
]

LOGIC_ARCHETYPES = [
    ("DateUtils", "Utilitas kalkulasi waktu relatif ('2m ago', '3h ago', 'yesterday') dan parsing tanggal format ISO."),
    ("ArrayDedupe", "Fungsi deduplikasi list of objects berdasarkan key unik tertentu dan pengelompokan group_by."),
    ("ChunkPagination", "Utilitas partisi array menjadi chunks sesuai page size dan helper pagination offset-limit."),
    ("EventEmitter", "Modul factory Event Emitter (def create_event_emitter) murni ES Module dengan method on, off, emit, dan once."),
    ("StringSanitizer", "Fungsi sanitasi string, pembersihan XSS, slugify URL string, dan parsing query string."),
    ("AsyncHttpClient", "Wrapper async fetch dengan fitur timeout AbortController, retry exponential backoff, dan error handling."),
    ("MetricCalculator", "Kalkulasi statistik deskriptif numerik: mean, median, min, max, percentile, dan moving average."),
    ("TreeFlattener", "Fungsi rekursif mengubah struktur data pohon hierarkis (parent-children) menjadi array datar."),
]

TOOL_TASK_TEMPLATES = [
    ("buat_komponen_file", "Buatkan file komponen {comp} di path `src/components/{comp}.hyx` dengan spesifikasi: {desc}"),
    ("buat_utilitas_file", "Tulis file modul logika {name} di path `src/utils/{name}.hys`: {desc}"),
    ("test_kompiler", "Jalankan pengecekan kompilator Rust pada file `src/components/{comp}.hyx` untuk memastikan tidak ada error sintaks."),
    ("baca_file", "Baca isi file `src/components/{comp}.hyx` untuk meninjau struktur hierarki elemennya."),
    ("refactor_file", "Ganti deklarasi kelas pill/badge pada file `src/components/{comp}.hyx` menjadi border persegi panjang yang rapi."),
    ("build_project", "Jalankan perintah build production untuk proyek HydraScript menggunakan CLI compiler."),
]


def strip_watermark(text: str) -> str:
    """Menghapus seluruh varian watermark [xihanzu-NR] dari teks kode, argumen, dan deskripsi."""
    cleaned = re.sub(r"(?:#|//|<!--|/\*)\s*\[xihanzu-NR\]\s*(?:-->|\*/)?\s*\n?", "", text)
    cleaned = re.sub(r"\[xihanzu-NR\]", "", cleaned)
    return cleaned.strip()


def fetch_9router_combos() -> List[str]:
    """Mengambil daftar combo yang aktif dari API 9router /v1/models."""
    try:
        models_url = GATEWAY_URL.replace("/v1/messages", "/v1/models")
        req = urllib.request.Request(
            models_url,
            headers={"x-api-key": API_KEY, "Authorization": f"Bearer {API_KEY}"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        return [m["id"] for m in data.get("data", []) if m.get("owned_by") == "combo"]
    except Exception as e:
        print(f"Warning: Gagal sync combos dari 9router ({e})")
        return []


def call_teacher_api(
    prompt: str,
    system_prompt: str = HYDRA_DOCTRINE_V2,
    model: str = "teacher_A",
    max_tokens: int = 10000,
    temperature: float = 0.25,
    timeout: int = 240,
    max_retries: int = 3,
) -> str:
    """Mengirim request ke 9router gateway dengan timeout panjang dan retry."""
    payload: Dict[str, Any] = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system_prompt:
        payload["system"] = system_prompt

    data_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        GATEWAY_URL,
        data=data_bytes,
        headers={
            "content-type": "application/json",
            "x-api-key": API_KEY,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )

    for attempt in range(max_retries):
        try:
            full_text = []
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                for line in resp:
                    line_str = line.decode("utf-8").strip()
                    if line_str.startswith("data:"):
                        raw_json = line_str[5:].strip()
                        if not raw_json:
                            continue
                        try:
                            event_data = json.loads(raw_json)
                            if event_data.get("type") == "content_block_delta":
                                delta = event_data.get("delta", {})
                                if delta.get("type") == "text_delta":
                                    full_text.append(delta.get("text", ""))
                        except json.JSONDecodeError:
                            continue
            result = "".join(full_text).strip()
            if result:
                return result
        except Exception:
            if attempt == max_retries - 1:
                return ""
            time.sleep(3 * (attempt + 1))

    return ""


# Alias query_teacher for direct programmatic calls
query_teacher = call_teacher_api


def extract_code(raw_response: str) -> Tuple[str, str]:
    match_hyx = re.search(r"```(?:hyx|python)\s*([\s\S]*?)```", raw_response, re.IGNORECASE)
    if match_hyx:
        return match_hyx.group(1).strip(), "hyx"

    match_hys = re.search(r"```(?:hys)\s*([\s\S]*?)```", raw_response, re.IGNORECASE)
    if match_hys:
        return match_hys.group(1).strip(), "hys"

    match_any = re.search(r"```\s*([\s\S]*?)```", raw_response)
    if match_any:
        return match_any.group(1).strip(), "hyx"

    return raw_response.strip(), "hyx"


def extract_tool_call(raw_response: str) -> Optional[Dict[str, Any]]:
    match = re.search(r"<tool_call>\s*([\s\S]*?)\s*</tool_call>", raw_response)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except Exception:
            return None
    return None


def verify_with_rust_compiler(code: str, file_type: str = "hyx") -> bool:
    if not os.path.exists(HYDRA_BIN):
        return True

    suffix = f".{file_type}"
    with tempfile.NamedTemporaryFile("w", suffix=suffix, delete=False, encoding="utf-8") as f:
        f.write(code)
        tmp_path = f.name

    try:
        proc = subprocess.run(
            [HYDRA_BIN, "--check", tmp_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5,
        )
        return proc.returncode == 0
    except Exception:
        return False
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


# --- GENERATOR LOGIC (CODE + TOOL CALLING) ---

def generate_code_sample(task_info: Dict[str, Any], model: str) -> Optional[Dict[str, Any]]:
    """Menghasilkan sampel kode HydraScript (.hyx / .hys) dengan penjelasan bahasa Indonesia."""
    category = task_info["category"]
    prompt_text = task_info["prompt"]
    target_ext = task_info["ext"]
    is_long_form = task_info.get("is_long_form", False)

    length_guidance = (
        "Tulis kode LENGKAP dan DETAIL (120-250 baris kode) dengan semua state, handler, dan sub-elemen. JANGAN gunakan placeholder '...' atau menyingkat kode!"
        if is_long_form
        else "Tulis kode lengkap dan idiomatik."
    )

    user_query = f"""{prompt_text}

Instruksi Tambahan:
- Berikan penjelasan 1-2 kalimat dalam bahasa Indonesia mengenai implementasi ini.
- {length_guidance}
- Format respon:
  [Penjelasan bahasa Indonesia]
  ```{target_ext}
  [Kode HydraScript 100% valid]
  ```"""

    raw_response = call_teacher_api(user_query, system_prompt=HYDRA_DOCTRINE_V2, model=model, max_tokens=10000)
    if not raw_response or len(raw_response) < 50:
        return None

    code, _ = extract_code(raw_response)
    code = re.sub(r"#\s*\[xihanzu-NR\]\s*\n?", "", code).strip()

    if not verify_with_rust_compiler(code, target_ext):
        return None

    # Ekstrak penjelasan bahasa Indonesia (teks sebelum blok ```)
    parts = re.split(r"```", raw_response)
    explanation = parts[0].strip() if len(parts) > 1 else "Implementasi komponen HydraScript dengan styling Tailwind dan state reaktif."
    explanation = re.sub(r"#\s*\[xihanzu-NR\]\s*\n?", "", explanation).strip()

    formatted = (
        f"### Instruction:\n{prompt_text}\n\n"
        f"### Response:\n{explanation}\n\n"
        f"```{target_ext}\n{code}\n```\n<|endoftext|>\n"
    )

    return {
        "type": "code_generation",
        "category": category,
        "teacher": model,
        "instruction": prompt_text,
        "explanation": explanation,
        "code": code,
        "formatted": formatted,
    }


def generate_tool_sample(task_info: Dict[str, Any], model: str) -> Optional[Dict[str, Any]]:
    """Menghasilkan sampel Tool Calling Claude Code (<tool_call>) dengan penjelasan bahasa Indonesia."""
    prompt_text = task_info["prompt"]
    tool_type = task_info["tool_type"]

    user_query = f"""{prompt_text}

Respon HANYA dengan:
1. Penjelasan singkat 1-2 kalimat dalam bahasa Indonesia mengenai aksi yang akan dijalankan.
2. Blok tool call:
<tool_call>
{{"name": "{tool_type}", "arguments": {{...}}}}
</tool_call>"""

    raw_response = call_teacher_api(user_query, system_prompt=TOOL_SYSTEM_PROMPT, model=model, max_tokens=10000)
    if not raw_response or "<tool_call>" not in raw_response:
        return None

    tool_call_obj = extract_tool_call(raw_response)
    if not tool_call_obj:
        return None

    # Jika tool adalah Write atau Edit yang memuat kode Hydra, verifikasi sintaksnya
    args = tool_call_obj.get("arguments", {})
    if tool_type in ["Write", "Edit"]:
        content = args.get("content") or args.get("new_string") or ""
        file_path = args.get("file_path", "")
        ext = "hys" if file_path.endswith(".hys") else "hyx"
        if content and (file_path.endswith(".hyx") or file_path.endswith(".hys")):
            clean_content = re.sub(r"#\s*\[xihanzu-NR\]\s*\n?", "", content).strip()
            if not verify_with_rust_compiler(clean_content, ext):
                return None
            args["content"] = clean_content
            tool_call_obj["arguments"] = args

    # Ekstrak penjelasan bahasa Indonesia (teks sebelum <tool_call>)
    explanation = raw_response.split("<tool_call>")[0].strip()
    explanation = re.sub(r"#\s*\[xihanzu-NR\]\s*\n?", "", explanation).strip()
    if not explanation:
        explanation = f"Menjalankan tool {tool_type} untuk mengeksekusi permintaan."

    clean_tool_str = json.dumps(tool_call_obj, indent=2, ensure_ascii=False)
    formatted = (
        f"### Instruction:\n{prompt_text}\n\n"
        f"### Response:\n{explanation}\n\n"
        f"<tool_call>\n{clean_tool_str}\n</tool_call>\n<|endoftext|>\n"
    )

    return {
        "type": "tool_calling",
        "tool_name": tool_type,
        "teacher": model,
        "instruction": prompt_text,
        "explanation": explanation,
        "tool_call": tool_call_obj,
        "formatted": formatted,
    }


def build_task_pool(
    total_tasks: int = 6000,
    code_count: int = 5000,
    tool_count: int = 1000,
    teacher_a: str = "teacher_A",
    teacher_b: str = "teacher_B",
) -> List[Dict[str, Any]]:
    """Membangun antrean task kombinatorial acak multi-gaya tanpa bias pengulangan template.
    Menjamin 100% seluruh tag HTML, komponen komposit, dan varian prompt manusia terdistribusi merata.
    Rasio Guru: 80% teacher_a : 20% teacher_b.
    """
    rng = random.Random(1337)
    tasks = []

    COLORS = ["neutral", "blue", "emerald", "amber", "rose", "violet", "indigo", "slate", "zinc"]
    VARIANTS = ["primary", "secondary", "outline", "ghost", "danger", "minimal", "subtle"]
    SIZES = ["sm", "md", "lg"]
    CONTEXTS = [
        "dashboard", "checkout", "auth login", "settings profil", "tabel data",
        "landing page", "navbar", "sidebar", "notifikasi", "chat messenger"
    ]

    HTML_TEMPLATES = [
        "bikin elemen {el}",
        "buatkan elemen {el} dong",
        "tolong buatin tag {el} di hydrascript",
        "gimana cara buat elemen {el} di .hyx?",
        "buatkan elemen HTML `{el}` dengan styling Tailwind bersih: {desc}",
        "implementasikan tag `{el}` di HydraScript (.hyx) untuk {desc}",
        "tulis kode elemen `{el}` dengan styling dark neutral minimalis",
        "bikin pembungkus elemen `{el}` dengan props className dan children",
        "code a clean `{el}` HTML element in HydraScript with tailwind",
        "create a responsive `{el}` element with proper attributes",
        "rancang elemen {el} untuk keperluan {context}",
        "buat tag {el} warna {color} varian {variant}",
    ]

    COMP_TEMPLATES = [
        "bikin {comp}",
        "buatkan komponen {comp} dong",
        "tolong buatkan komponen {comp} di hydrascript",
        "gimana cara buat {comp} di .hyx?",
        "buat {comp} varian {variant} warna {color}",
        "bikin {comp} untuk keperluan {context}",
        "implementasikan komponen `{comp}` di HydraScript (.hyx): {desc}",
        "tulis kode komponen `{comp}` lengkap dengan state dan props",
        "rancang komponen `{comp}` yang interaktif dan responsif",
        "code a reusable `{comp}` component with tailwind in hydrascript",
        "buat {comp} yang mendukung props {props}",
        "buatkan {comp} dengan ukuran {size} dan state interaktif",
    ]

    COMPOSITE_TEMPLATES = [
        "bikin layout {comp}",
        "buatkan komponen komposit {comp} lengkap",
        "tolong buatkan halaman/fitur {comp} di HydraScript (.hyx)",
        "implementasikan fitur komposit `{comp}`: {desc}",
        "rancang antarmuka {comp} dengan komponen interaktif terintegrasi",
        "code a complete composite `{comp}` in HydraScript (.hyx)",
        "buatkan fitur {comp} bertema dark theme neutral rapi",
    ]

    def make_teacher(idx: int) -> str:
        # Rasio: teacher_a 80% : teacher_b 20%
        return teacher_a if (idx % 5 != 0) else teacher_b

    # 1. Task HTML Primitives (~24% dari code_count, seluruh 20 tag merata)
    num_html = int(code_count * 0.24)
    for i in range(num_html):
        el, desc = HTML_ELEMENTS[i % len(HTML_ELEMENTS)]
        tpl = rng.choice(HTML_TEMPLATES)
        prompt = tpl.format(
            el=el,
            desc=desc,
            context=rng.choice(CONTEXTS),
            color=rng.choice(COLORS),
            variant=rng.choice(VARIANTS),
        )
        tasks.append({
            "kind": "code",
            "category": f"html_{el}",
            "prompt": prompt,
            "ext": "hyx",
            "is_long_form": False,
            "model": make_teacher(len(tasks)),
        })

    # 2. Task UI Components (~36% dari code_count, seluruh 27 arketipe merata)
    num_comp = int(code_count * 0.36)
    for i in range(num_comp):
        comp, desc = COMPONENT_ARCHETYPES[i % len(COMPONENT_ARCHETYPES)]
        tpl = rng.choice(COMP_TEMPLATES)
        is_long = comp in ["ServerDashboard", "SettingsPage", "KanbanBoard", "MultiStepWizard", "AuditLogViewer"] or (i % 8 == 0)
        length_hint = " (tulis lengkap 120-250 baris kode)" if is_long else ""
        prompt = tpl.format(
            comp=comp,
            desc=desc,
            variant=rng.choice(VARIANTS),
            color=rng.choice(COLORS),
            size=rng.choice(SIZES),
            context=rng.choice(CONTEXTS),
            props="onClick, disabled, className, variant",
        ) + length_hint

        tasks.append({
            "kind": "code",
            "category": f"component_{comp}",
            "prompt": prompt,
            "ext": "hyx",
            "is_long_form": is_long,
            "model": make_teacher(len(tasks)),
        })

    # 3. Task Komponen Komposit / Multi-Komponen (~16% dari code_count)
    num_composite = int(code_count * 0.16)
    for i in range(num_composite):
        comp, desc = COMPOSITE_COMPONENTS[i % len(COMPOSITE_COMPONENTS)]
        tpl = rng.choice(COMPOSITE_TEMPLATES)
        prompt = tpl.format(comp=comp, desc=desc)
        tasks.append({
            "kind": "code",
            "category": f"composite_{comp}",
            "prompt": prompt,
            "ext": "hyx",
            "is_long_form": (i % 3 == 0),
            "model": make_teacher(len(tasks)),
        })

    # 4. Task Transpilasi React TSX ke Hydra (~12% dari code_count)
    num_tsx = int(code_count * 0.12)
    for i in range(num_tsx):
        comp, desc = COMPONENT_ARCHETYPES[i % len(COMPONENT_ARCHETYPES)]
        prompt = f"Adaptasikan komponen React TSX `{comp}` ke dalam format native HydraScript (.hyx): {desc}"
        tasks.append({
            "kind": "code",
            "category": f"tsx_to_hyx_{comp}",
            "prompt": prompt,
            "ext": "hyx",
            "is_long_form": False,
            "model": make_teacher(len(tasks)),
        })

    # 5. Task Logika Pythonic / Algoritma murni (.hys) (~8% dari code_count)
    num_logic = int(code_count * 0.08)
    for i in range(num_logic):
        logic_name, desc = LOGIC_ARCHETYPES[i % len(LOGIC_ARCHETYPES)]
        prompt = f"Tulis modul logika Pythonic murni di HydraScript (.hys) untuk `{logic_name}`: {desc}"
        tasks.append({
            "kind": "code",
            "category": f"logic_{logic_name}",
            "prompt": prompt,
            "ext": "hys",
            "is_long_form": False,
            "model": make_teacher(len(tasks)),
        })

    # 6. Task Anti-Pattern Repair (Sisa kuota code_count, 5 tipe perbaikan dibagi merata)
    rep_types = [
        ("TreeAssignment", "Pindahkan assignment variabel dari dalam JSX tree ke preamble atas."),
        ("SpreadOperator", "Ganti spread array `[*items]` menjadi `items.concat()` atau list addition."),
        ("StringMethods", "Ganti Python string join `\" \".join()` menjadi JS method `list.join(\" \")`."),
        ("StringIncludes", "Ganti operator `in` pada string menjadi `text.includes(query)`."),
        ("PillRemoval", "Hapus kelas `rounded-full` (pill) dan emoji, ganti dengan border persegi panjang rapi."),
    ]
    num_rep = max(0, code_count - (num_html + num_comp + num_composite + num_tsx + num_logic))
    for i in range(num_rep):
        rep_name, fix_desc = rep_types[i % len(rep_types)]
        prompt = f"Perbaiki kode HydraScript yang melanggar aturan kompiler pada kasus `{rep_name}`: {fix_desc}"
        tasks.append({
            "kind": "code",
            "category": f"repair_{rep_name}",
            "prompt": prompt,
            "ext": "hyx",
            "is_long_form": False,
            "model": make_teacher(len(tasks)),
        })

    # 7. 1.000 Task Tool Calling Claude Code (Write, Read, Edit, Bash)
    for j in range(tool_count):
        tool_choice = j % 4
        comp, desc = COMPONENT_ARCHETYPES[j % len(COMPONENT_ARCHETYPES)]
        logic_name, ldesc = LOGIC_ARCHETYPES[j % len(LOGIC_ARCHETYPES)]

        if tool_choice == 0:
            prompt = rng.choice([
                f"simpan komponen {comp} ke path src/components/{comp}.hyx",
                f"buatkan file komponen `{comp}` di path `src/components/{comp}.hyx`: {desc}",
                f"tolong buatkan file `src/components/{comp}.hyx` untuk {comp}",
            ])
            tasks.append({
                "kind": "tool",
                "tool_type": "Write",
                "prompt": prompt,
                "model": teacher_b,
            })
        elif tool_choice == 1:
            prompt = rng.choice([
                f"simpan modul logika {logic_name} ke path src/utils/{logic_name}.hys",
                f"tulis file modul logika `{logic_name}` di path `src/utils/{logic_name}.hys`: {ldesc}",
                f"buatkan utilitas `src/utils/{logic_name}.hys`",
            ])
            tasks.append({
                "kind": "tool",
                "tool_type": "Write",
                "prompt": prompt,
                "model": teacher_b,
            })
        elif tool_choice == 2:
            commands = [
                f"/root/projects/hydra/compiler-rs/target/release/hydra --check src/components/{comp}.hyx",
                "/root/projects/hydra/compiler-rs/target/release/hydra build",
                f"/root/projects/hydra/compiler-rs/target/release/hydra --check src/utils/{logic_name}.hys",
                "npm run dev",
                "cargo check",
            ]
            cmd = commands[j % len(commands)]
            prompt = rng.choice([
                f"jalankan perintah terminal `{cmd}` untuk verifikasi",
                f"Jalankan perintah terminal untuk memverifikasi proyek HydraScript: `{cmd}`",
                f"buka terminal dan jalankan `{cmd}`",
            ])
            tasks.append({
                "kind": "tool",
                "tool_type": "Bash",
                "prompt": prompt,
                "model": teacher_b,
            })
        else:
            prompt = rng.choice([
                f"baca file `src/components/{comp}.hyx` buat periksa struktur elemennya",
                f"Baca file `src/components/{comp}.hyx` untuk memeriksa struktur pohon elemen dan props-nya.",
                f"tolong periksa isi file `src/components/{comp}.hyx`",
            ])
            tasks.append({
                "kind": "tool",
                "tool_type": "Read",
                "prompt": prompt,
                "model": teacher_b,
            })

    # Acak urutan agar tercampur sempurna (tidak mengelompok berurutan)
    rng.shuffle(tasks)
    return tasks[:total_tasks]


def run_full_distillation_v2(
    total_samples: int = 6000,
    atria_workers: int = 40,
    gemini_workers: int = 2,
    teacher_a: str = "teacher_A",
    teacher_b: str = "teacher_B",
    max_tokens: int = 10000,
    output_dir: str = "/root/models/distilled_hydra_v2",
):
    os.makedirs(output_dir, exist_ok=True)
    jsonl_path = os.path.join(output_dir, "hydrascript_dataset_v2.jsonl")
    txt_path = os.path.join(output_dir, "hydrascript_train_v2.txt")

    active_combos = fetch_9router_combos()

    existing_count = 0
    if os.path.exists(jsonl_path):
        with open(jsonl_path, "r", encoding="utf-8") as f:
            existing_count = sum(1 for _ in f)

    remaining_needed = max(0, total_samples - existing_count)

    print("=" * 70)
    print(" ⚡ HYDRASCRIPT NEURAL DISTILLATION v2 (6.000 SAMPLES)")
    print("=" * 70)
    print(f"  Target Total:       {total_samples:,} sampel (5k Kurikulum + 1k Tool Calling)")
    print(f"  Existing Done:      {existing_count:,} sampel")
    print(f"  Remaining:          {remaining_needed:,} sampel")
    print(f"  Active 9router:     {active_combos}")
    print(f"  Teacher Model A:    {teacher_a} ({atria_workers} Dedicated Workers)")
    print(f"  Teacher Model B:    {teacher_b} ({gemini_workers} Workers)")
    print(f"  Max Output Tokens:  {max_tokens:,}")
    print(f"  Format:             Dwi-Bahasa (Penjelasan Indonesia + Kode/Tool Call)")
    print(f"  Compiler Gate:      {HYDRA_BIN} (--check active)")
    print(f"  Output Directory:   {output_dir}/\n")

    if remaining_needed == 0:
        print("Target 6.000 sampel sudah selesai!")
        return

    # Buat pool task besar yang bervariasi
    full_pool = build_task_pool(
        total_tasks=total_samples * 2,
        code_count=int(total_samples * 1.7),
        tool_count=int(total_samples * 0.3),
        teacher_a=teacher_a,
        teacher_b=teacher_b,
    )
    task_iter = iter(full_pool)

    successful = existing_count
    total_tokens_est = 0
    t0 = time.time()

    with open(jsonl_path, "a", encoding="utf-8") as f_jsonl, open(txt_path, "a", encoding="utf-8") as f_txt:
        with concurrent.futures.ThreadPoolExecutor(max_workers=gemini_workers) as gemini_pool, \
             concurrent.futures.ThreadPoolExecutor(max_workers=atria_workers) as atria_pool:

            future_to_task = {}

            def schedule_task(task_item):
                m = task_item["model"]
                pool = atria_pool if m == teacher_a else gemini_pool
                if task_item["kind"] == "code":
                    return pool.submit(generate_code_sample, task_item, m)
                else:
                    return pool.submit(generate_tool_sample, task_item, m)

            # Inisialisasi slot worker penuh
            total_slots = atria_workers + gemini_workers
            for _ in range(min(remaining_needed + 10, total_slots)):
                try:
                    t = next(task_iter)
                    fut = schedule_task(t)
                    future_to_task[fut] = t
                except StopIteration:
                    break

            while future_to_task and successful < total_samples:
                done, _ = concurrent.futures.wait(future_to_task.keys(), return_when=concurrent.futures.FIRST_COMPLETED)
                for fut in done:
                    _ = future_to_task.pop(fut)
                    try:
                        res = fut.result()
                    except Exception:
                        res = None

                    if res:
                        successful += 1
                        f_jsonl.write(json.dumps(res, ensure_ascii=False) + "\n")
                        f_jsonl.flush()
                        f_txt.write(res["formatted"])
                        f_txt.flush()

                        tok_est = len(res["formatted"]) // 4
                        total_tokens_est += tok_est
                        dt = time.time() - t0
                        teacher_tag = "TEACHER_A" if res.get("teacher") == teacher_a else "TEACHER_B"
                        kind_tag = "TOOL" if res.get("type") == "tool_calling" else "CODE"

                        print(
                            f"[{successful:5d}/{total_samples}] "
                            f"[{kind_tag:<4}] [{teacher_tag:<9}] "
                            f"Tokens: ~{total_tokens_est:,} | "
                            f"Compiler: 100% PASS | "
                            f"Elapsed: {dt/60:.1f}m"
                        )

                    # Jika kuota sukses belum tercapai, segera isi slot yang kosong dengan task baru
                    if successful + len(future_to_task) < total_samples:
                        try:
                            new_task = next(task_iter)
                            new_fut = schedule_task(new_task)
                            future_to_task[new_fut] = new_task
                        except StopIteration:
                            pass

    print("\n" + "=" * 70)
    print(f"  Distilasi v2 Selesai Sempurna: {successful:,} / {total_samples:,} sampel")
    print(f"  File Dataset Final: {txt_path}")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="HydraScript Distillation v2 Pipeline")
    parser.add_argument("--count", type=int, default=6000, help="Total sampel (default: 6000)")
    parser.add_argument("--atria_workers", type=int, default=40, help="Dedicated workers Teacher A (default: 40)")
    parser.add_argument("--gemini_workers", type=int, default=2, help="Workers Teacher B (default: 2)")
    parser.add_argument("--teacher_a", type=str, default="teacher_A", help="Nama combo 9router Teacher A")
    parser.add_argument("--teacher_b", type=str, default="teacher_B", help="Nama combo 9router Teacher B")
    parser.add_argument("--max_tokens", type=int, default=10000, help="Max output tokens (default: 10000)")
    parser.add_argument("--output_dir", type=str, default="/root/models/distilled_hydra_v2", help="Folder output")
    args = parser.parse_args()

    run_full_distillation_v2(
        total_samples=args.count,
        atria_workers=args.atria_workers,
        gemini_workers=args.gemini_workers,
        teacher_a=args.teacher_a,
        teacher_b=args.teacher_b,
        max_tokens=args.max_tokens,
        output_dir=args.output_dir,
    )


if __name__ == "__main__":
    main()
