# Architecture

## Overview

Signal Horizon is a custom UI layer built on top of ACE-Step 1.5, providing a streamlined music generation experience.

```
┌─────────────────────────────────────────────────────────┐
│                    Signal Horizon UI                     │
│                     (index.html)                         │
├─────────────────────────────────────────────────────────┤
│                   FastAPI Server                         │
│              (model_server.py / launcher.py)            │
├──────────────────────┬──────────────────────────────────┤
│     API Routes       │        Static Files              │
│   (/api/*)           │      (/, /static/*)              │
├──────────────────────┴──────────────────────────────────┤
│                  ACE-Step Engine                         │
├─────────────────────┬───────────────────────────────────┤
│    DiT Handler      │         LLM Handler               │
│  (Music Generation) │    (Lyrics/Caption Processing)   │
├─────────────────────┴───────────────────────────────────┤
│                    GPU / CUDA                            │
└─────────────────────────────────────────────────────────┘
```

## Components

### Signal Horizon Layer

| Component | File | Purpose |
|-----------|------|---------|
| Clean UI | `index.html` | Modern web interface |
| Model Server | `model_server.py` | Hot-reload capable server |
| Launcher | `launcher.py` | Production with Gradio |
| Full Launcher | `launcher_full.py` | Complete Gradio UI |

### ACE-Step Layer

| Component | Purpose |
|-----------|---------|
| `AceStepHandler` | DiT model for audio generation |
| `LLMHandler` | 5Hz LM for lyrics/caption processing |
| `api_routes.py` | REST API endpoints |
| `gpu_config.py` | Tier-based GPU optimization |

## Data Flow

### Music Generation Request

```
1. User enters prompt in UI
2. UI sends POST to /api/release_task
3. Server extracts parameters
4. If sample_mode: LLM generates caption/lyrics
5. DiT generates audio
6. Audio saved to temp directory
7. Response includes download URL
8. UI fetches audio via /api/v1/audio
```

## Model Architecture

### DiT (Diffusion Transformer)
- Generates music from text descriptions
- Handles: genre, BPM, key, duration
- Output: WAV/MP3 audio files

### 5Hz LM (Language Model)
- Enhances prompts and generates lyrics
- Features: sample_mode, format_input
- Optional but enables advanced features

## Port Convention

**Port 8372** = ASCII values of 'SH' (Signal Horizon)
- S = 83
- H = 72
- Combined: 8372

This ensures a unique, memorable port that won't conflict with common services.
