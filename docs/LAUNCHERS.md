# Signal Horizon Launchers

## Quick Start

| Launcher | Startup | Best For |
|----------|---------|----------|
| **Signal Horizon.bat** | ~2 min | Normal use, fast generation |
| **Signal Horizon (Dev).bat** | ~1 min | UI development, quick testing |
| **Signal Horizon (Full).bat** | ~3 min | Gradio UI, all ACE-Step features |

---

## Understanding the Two-Model Architecture

Signal Horizon uses **ACE-Step 1.5** which has two AI models:

### DiT (Diffusion Transformer) - Required
- **What it does**: Generates actual audio from your caption/lyrics
- **Speed**: Fast (~20-60s per track)
- **Always loaded**: All launchers use DiT

### LLM (5Hz Language Model) - Optional
- **What it does**: Enhances prompts, detects language, generates "audio codes"
- **Speed**: Slow (1-5+ minutes)
- **When useful**: Complex prompts, highest quality output
- **Modes**:
  - **CoT (Chain of Thought)**: Auto-enriches caption, detects language
  - **Thinking Mode**: Generates semantic audio codes for precise control

---

## Launcher Details

### Signal Horizon.bat (Recommended)
```
DiT: ✅ Loaded
LLM: ✅ Loaded (but CoT disabled by default)
```
- Fast generation using DiT
- LLM available if you enable "Thinking Mode"
- Best balance of speed and capability

### Signal Horizon (Dev).bat
```
DiT: ✅ Loaded
LLM: ❌ Skipped
```
- Fastest startup
- Edit `index.html` → refresh browser
- Music generation works (DiT only)
- "Thinking Mode" unavailable

### Signal Horizon (Full).bat
```
DiT: ✅ Loaded  
LLM: ✅ Loaded (with CoT enabled)
```
- Original Gradio interface
- All advanced modes (Cover, Repaint, Lego)
- Slowest but most feature-complete

---

## Generation Speed Reference

| Duration | DiT Only | DiT + LLM (Thinking) |
|----------|----------|---------------------|
| 30s | ~20s | ~2 min |
| 60s | ~40s | ~3 min |
| 120s | ~80s | ~5 min |

*Times approximate, depends on GPU and settings*
