# Quick Start Guide

Get Signal Horizon running in 5 minutes.

## Prerequisites

- Windows 10/11
- NVIDIA GPU with 8GB+ VRAM (RTX 3070 or better recommended)
- [uv](https://github.com/astral-sh/uv) package manager installed

## Step 1: First Launch

Double-click **`Signal Horizon.bat`**

Wait for models to load (~2-3 minutes first time). You'll see:
```
✓ DiT model loaded!
✓ LLM model loaded!
✧ Signal Horizon ready!
```

## Step 2: Open the UI

Browser opens automatically to: **http://127.0.0.1:8372**

## Step 3: Generate Music

1. **Enter a description:**
   ```
   upbeat electronic dance music with synth leads, 128 BPM
   ```

2. **Add lyrics (optional):**
   ```
   [verse]
   Dancing through the night
   Lights are shining bright
   ```

3. **Click Generate**

4. **Wait ~30-60 seconds** for AI to create your music

5. **Download** the generated audio files

## Tips

### For Faster Development

Use **`Signal Horizon (Dev).bat`** - models stay loaded while you edit code.

### For Advanced Features

Use **`Signal Horizon (Full).bat`** - full ACE-Step Gradio interface.

### Sample Prompts

| Genre | Example Prompt |
|-------|----------------|
| Pop | `catchy pop song, female vocals, uplifting chorus, 120 BPM` |
| EDM | `progressive house, building energy, festival anthem, 128 BPM` |
| Rock | `classic rock, electric guitar riffs, powerful drums, 110 BPM` |
| Lo-Fi | `lo-fi hip hop, jazzy chords, vinyl crackle, chill vibes, 85 BPM` |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Models won't load | Check GPU has enough VRAM (8GB+) |
| Generation fails | Try shorter duration or simpler prompt |
| No audio output | Check browser console for errors |
| Port in use | Close other servers on port 8372 |

## Next Steps

- Read [DEVELOPMENT.md](DEVELOPMENT.md) for code editing workflow
- Read [API.md](API.md) to integrate with other tools
- Explore [ARCHITECTURE.md](ARCHITECTURE.md) to understand the system
