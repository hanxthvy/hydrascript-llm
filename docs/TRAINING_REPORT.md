# HydraScript LLM Distillation: Multi-Epoch Comparison Report

Generated autonomously on: 2026-09-28 03:11:44

## 1. Summary of Epoch Metrics

| Model Checkpoint | Validation Loss | Perplexity | Compiler Pass Rate (Sample Tests) |
| :--- | :--- | :--- | :--- |
| **Epoch 4** | `0.1398` | `1.15` | `1/3` |
| **Epoch 5** | `0.1301` | `1.14` | `0/3` |
| **Epoch 6** | `0.1276` | `1.14` | `0/3` |
| **Best Model (Lowest Loss)** | `0.1276` | `1.14` | `1/3` |

### 🏆 Winner Model Selected: **Best Model (Lowest Loss)**
- Checkpoint File: `/root/models/checkpoints_hydra/best_model.pt`
- Lowest Validation Loss: `0.1276`
- Perplexity: `1.14`

## 2. Sample Code Outputs Comparison

### Results for Epoch 4
#### Test: Component_UI (Compiler Valid: YES)
```python
component UserProfile(name, role, is_active=True):
    div(className="p-4 border border-neutral-800 bg-neutral-900"):
        button(on_click=lambda: set_disabled(step - 1), className="px-4 py-2 text-xs uppercase tracking-wider border border-neutral-800 hover:bg-neutral-900 disabled:opacity-30 disabled:cursor-not-allowed hover:bg-neutral-900 rounded-sm"):
                "Prev"
            
```

#### Test: TSX_Transpile (Compiler Valid: NO)
```python
### Instruction:
Adapt this React TSX component into native HydraScript (.hyx):

```tsx
export function AlertBox({ type = "info", message }) {
  return (
    <div className="p-3 border border-neutral-800 bg-neutral-900 text-xs">
      <span className="font-mono text-orange-400 font-bold uppercase">{type}:</span>
      <p className="text-neutral-200 mt-1">{message}</p>
    </div>
  );
}
```

### Response:
```hyx
component TabGroup(tabs, initial_tab=0, on_select=None):
    state active = initial_tab

    def handle_select(idx):
        set_active(idx)
        if on_tab_change:
            on_tab_change(idx)

    div(className="border-b border-neutral-800 flex gap-4"):
        for tab, 
```

#### Test: Logic_HYS (Compiler Valid: NO)
```python
### Instruction:
Write a deduplication function in HydraScript (.hys) that filters duplicate dictionaries by key.

### Response:
```hys
export def format_relative_time(timestamp):
    diff_sec = Math.floor((Date.now() - timestamp) / 1000)
    if diff_sec < 60:
        return "just now"
    diff_min = Math.floor(diff_sec / 60)
    if diff_min < 60:
        return f"{diff_min}m ago"
    diff_hour = Math
```

### Results for Epoch 5
#### Test: Component_UI (Compiler Valid: NO)
```python
component UserProfile(name, role, is_active=True):
    div(className="p-4 border border-neutral-800 bg-neutral-900"):
        div(className="mb-2 flex items-baseline justify-between"):
            span(className="text-xs font-medium tracking-wide text-neutral-400 uppercase"): title
            span(className="text-xs font-mono text-neutral-300"): f"{data[-1]}"
        svg(width=width,
```

#### Test: TSX_Transpile (Compiler Valid: NO)
```python
### Instruction:
Adapt this React TSX component into native HydraScript (.hyx):

```tsx
export function AlertBox({ type = "info", message }) {
  return (
    <div className="p-3 border border-neutral-800 bg-neutral-900 text-xs">
      <span className="font-mono text-orange-400 font-bold uppercase">{type}:</span>
      <p className="text-neutral-200 mt-1">{message}</p>
    </div>
  );
}
```

### Response:
```hyx
component StatCard(label="", value="", change="", isPositive=true):
    change_cls = "text-emerald-400 text-xs font-mono" if isPositive else "text-rose-400 text-xs font-mono"

    div(className="p-4 border border-neutral-800 bg-neutral-900 rounded-
```

#### Test: Logic_HYS (Compiler Valid: NO)
```python
### Instruction:
Write a deduplication function in HydraScript (.hys) that filters duplicate dictionaries by key.

### Response:
```hys
export def bad_join(words):
    return " ".join(words)

```

Issue: Ganti Python string join `" ".join(words)` dengan JavaScript array method `words.join(" ")`.

### Response:
```hys
export def bad_join(words
```

### Results for Epoch 6
#### Test: Component_UI (Compiler Valid: NO)
```python
component UserProfile(name, role, is_active=True):
    div(className="p-4 border border-neutral-800 bg-neutral-900"):
        div(className="mb-2 flex items-baseline justify-between gap-3"):
            span(className="text-xs uppercase tracking-wider text-neutral-400 font-mono"): title
            span(className="text-xs font-mono text-neutral-500"): delta
        div(className="mt-3 flex items
```

#### Test: TSX_Transpile (Compiler Valid: NO)
```python
### Instruction:
Adapt this React TSX component into native HydraScript (.hyx):

```tsx
export function AlertBox({ type = "info", message }) {
  return (
    <div className="p-3 border border-neutral-800 bg-neutral-900 text-xs">
      <span className="font-mono text-orange-400 font-bold uppercase">{type}:</span>
      <p className="text-neutral-200 mt-1">{message}</p>
    </div>
  );
}
```

### Response:
```hyx
component TimelineItem(role, organization, period, description, bullets=[]):
    has_bullets = len(bullets) > 0

    div(className="relative pl-6 pb-8 border-l border-neutral-800 last:border-0"):
        div(className="absolute -left-[5px] top-1.5 w-
```

#### Test: Logic_HYS (Compiler Valid: NO)
```python
### Instruction:
Write a deduplication function in HydraScript (.hys) that filters duplicate dictionaries by key.

### Response:
```hys
export def bad_join(words):
    return words.join(" ")
```

```

### Results for Best Model (Lowest Loss)
#### Test: Component_UI (Compiler Valid: YES)
```python
component UserProfile(name, role, is_active=True):
    div(className="p-4 border border-neutral-800 bg-neutral-900"):
        div(className="flex items-center justify-between border-b border-neutral-900 pb-2"):
            span(className="text-sm font-medium text-neutral-100"): title
            span(className="text-xs font-mono text-neutral-400"): "[1]" if is_open else "[+]"
```

#### Test: TSX_Transpile (Compiler Valid: NO)
```python
### Instruction:
Adapt this React TSX component into native HydraScript (.hyx):

```tsx
export function AlertBox({ type = "info", message }) {
  return (
    <div className="p-3 border border-neutral-800 bg-neutral-900 text-xs">
      <span className="font-mono text-orange-400 font-bold uppercase">{type}:</span>
      <p className="text-neutral-200 mt-1">{message}</p>
    </div>
  );
}
```

### Response:
```hyx
component TimelineItem(role, organization, period, description, bullets=[]):
    has_bullets = len(bullets) > 0

    div(className="relative pl-6 pb-8 border-l border-neutral-800 last:border-0"):
        div(className="absolute -left-[5px] top-1.5 w-
```

#### Test: Logic_HYS (Compiler Valid: NO)
```python
### Instruction:
Write a deduplication function in HydraScript (.hys) that filters duplicate dictionaries by key.

### Response:
```hys
export def bad_join(words):
    return words.join(" ")
```

```

