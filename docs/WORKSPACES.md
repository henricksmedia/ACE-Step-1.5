# Signal Horizon: Advanced Workspaces

Signal Horizon provides specialized workspaces for different music production tasks, leveraging the full power of ACE-Step 1.5.

## Workspaces Overview

| Workspace | Purpose | Model | Status |
|-----------|---------|-------|--------|
| 🎵 **Studio** | Create new tracks from text/lyrics | Turbo | ✅ Complete |
| 🔧 **Remix Lab** | Transform songs to different styles | Turbo | ✅ Complete |
| ✂️ **Stem Ripper** | Extract individual instrument tracks | Base | ✅ Complete |
| 🧱 **Layer Builder** | Add instruments layer by layer | Base | 🔜 Planned |
| 🎛️ **Mastering** | Fix sections, extend tracks | Turbo/Base | 🔜 Planned |

> **Launcher Tip**: Use `Signal Horizon.bat` for Turbo features (fast). Use `Signal Horizon (Pro).bat` for Base features (Stem Ripper, etc.).

---

## 🔧 Remix Lab

Transform any song into a different style while keeping the melodic structure.

### How It Works

1. **Upload** a source track (any genre)
2. **Select** a target style (e.g., "Jazz Piano", "Lo-fi Electronic")
3. **Adjust** cover strength:
   - **High (0.8–1.0)**: Tight adherence to original structure
   - **Medium (0.4–0.7)**: Balanced transformation
   - **Low (0.1–0.3)**: Loose interpretation, more creative freedom
4. **Generate** and compare variations

### Use Cases

- **Genre Flip**: Rock → Acoustic Folk, Pop → Orchestral
- **Style Transfer**: Modern → Retro, Clean → Lo-fi
- **Cover Versions**: Create instrumental or re-sung versions
- **Remix Ideas**: Generate starting points for remixes

### API Reference

```
task_type: "cover"
src_audio: <uploaded file>
caption: <target style description>
audio_cover_strength: 0.0–1.0
lyrics: <optional new lyrics>
```

---

## 🧱 Layer Builder

Build complex arrangements by adding one instrument layer at a time.

### How It Works

1. **Upload** a base track (e.g., vocals, guitar)
2. **Select** a layer to add: drums, bass, synth, strings, etc.
3. **Describe** the desired style for that layer
4. **Generate** and repeat for additional layers

### Available Layers

`vocals` | `backing_vocals` | `drums` | `bass` | `guitar` | `keyboard` | `percussion` | `strings` | `synth` | `fx` | `brass` | `woodwinds`

### API Reference

```
task_type: "lego"
src_audio: <base track>
instruction: "Generate the {TRACK_NAME} track based on the audio context:"
caption: <layer style description>
```

**Requires**: Base model

---

## ✂️ Stem Ripper

Extract individual instrument tracks from mixed audio.

### How It Works

1. **Upload** a mixed track
2. **Select** the instrument to extract
3. **Generate** isolated stem

### API Reference

```
task_type: "extract"
src_audio: <mixed audio>
instruction: "Extract the {TRACK_NAME} track from the audio:"
```

**Requires**: Base model

**Note**: Uses diffusion-based extraction—results may differ from traditional source separation tools.

---

## 🎛️ Mastering

Fix problematic sections, extend tracks, or add missing instruments.

### Repaint Mode

Regenerate a specific time range:

```
task_type: "repaint"
src_audio: <track>
repainting_start: <seconds>
repainting_end: <seconds>
caption: <desired content>
```

### Auto-Complete Mode

Add missing instrument layers:

```
task_type: "complete"
src_audio: <partial track>
instruction: "Complete the input track with {TRACK_CLASSES}:"
caption: <style description>
```

**Requires**: Base model for complete task

---

## Model Requirements

| Model | Download Command | Features |
|-------|-----------------|----------|
| Turbo | Included by default | text2music, cover, repaint |
| Base | `uv run acestep-download --model acestep-v15-base` | extract, lego, complete |

---

## Quick Reference

| Action | Workspace | Task Type |
|--------|-----------|-----------|
| Create from scratch | Studio | `text2music` |
| Change genre/style | Remix Lab | `cover` |
| Add instrument layer | Layer Builder | `lego` |
| Extract stem | Stem Ripper | `extract` |
| Fix section | Mastering | `repaint` |
| Add accompaniment | Mastering | `complete` |
