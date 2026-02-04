# Signal Horizon Troubleshooting

## Critical Issues & Fixes

---

### ⚠️ Generation Stuck at 0% / Extremely Slow

**Symptoms:**
- Console shows `Generating: 0%` for minutes
- `Prefill=9tok/s` instead of `Prefill=200tok/s`
- torch.dynamo warnings about "tensor rank mismatch"
- Generation that used to take 20s now takes 5+ minutes

**Root Cause:**
The `GenerationParams` dataclass in `acestep/inference.py` has these defaults:
```python
thinking: bool = True
use_cot_metas: bool = True
use_cot_caption: bool = True
use_cot_language: bool = True
```

If your API code doesn't explicitly set these to `False`, the LLM's Chain-of-Thought reasoning is **always triggered**, making generation extremely slow.

**Solution:**
In `acestep/gradio_ui/api_routes.py`, the `GenerationParams` constructor MUST include:
```python
params = GenerationParams(
    # ... other params ...
    thinking=False,              # CRITICAL
    use_cot_metas=False,         # CRITICAL
    use_cot_caption=False,       # CRITICAL
    use_cot_language=False,      # CRITICAL
)
```

**Prevention:**
- Always explicitly set CoT params when using the API
- Default to `False` for fast DiT-only generation
- Only enable CoT when user selects "Thinking Mode" in UI

---

### LLM Model Not Found / Wrong Path

**Symptoms:**
```
⚠ LLM initialization failed: ❌ 5Hz LM model not found at 
D:\...\ACE-Step-1.5\ACE-Step-1.5\checkpoints\acestep-5Hz-lm-1.7B
```
(Note the duplicated `ACE-Step-1.5\ACE-Step-1.5`)

**Root Cause:**
In launcher files, the `ACESTEP_PATH` was incorrectly set:
```python
# WRONG - creates duplicate path
ACESTEP_PATH = os.path.join(os.path.dirname(__file__), "..", "ACE-Step-1.5")

# CORRECT - parent is already ACE-Step-1.5
ACESTEP_PATH = os.path.join(os.path.dirname(__file__), "..")
```

**Solution:**
Check all launcher files (`launcher.py`, `launcher_full.py`, `server.py`) and ensure:
```python
ACESTEP_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
```

---

### torch.dynamo Recompilation Warnings

**Symptoms:**
```
torch._dynamo hit config.recompile_limit (8)
tensor 'x' rank mismatch. expected 2, actual 3
```

**Cause:**
Dynamic tensor shapes (batch size changes, varying duration) cause torch.compile to recompile repeatedly.

**Solution:**
These are warnings, not errors. Generation will still complete, just slower on first run. To suppress:
```python
import torch._dynamo
torch._dynamo.config.suppress_errors = True
```

---

## Quick Diagnostics

| Issue | Check | Fix |
|-------|-------|-----|
| Slow generation | Console shows `Prefill=9tok/s` | Set CoT params to False |
| Model not found | Path has duplicate folders | Fix ACESTEP_PATH |
| UI stuck at 0% | Console shows no output | Check CORS, API endpoints |
| Cancel doesn't stop | Backend still running | Cancel only stops polling, not backend |

---

## File Reference

| File | Purpose |
|------|---------|
| `acestep/inference.py` | GenerationParams defaults (lines 126-136) |
| `acestep/gradio_ui/api_routes.py` | API parameter handling (lines 576-596) |
| `signal-horizon/launcher.py` | Normal launcher |
| `signal-horizon/launcher_full.py` | Gradio launcher |
| `signal-horizon/server.py` | Dev server |
