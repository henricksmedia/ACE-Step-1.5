# Admin Settings Reference

**Language / 语言 / 言語:** [English](ADMIN_SETTINGS.md) | [中文](../zh/ADMIN_SETTINGS.md) | [日本語](../ja/ADMIN_SETTINGS.md)

---

This guide provides comprehensive documentation of all Signal Horizon admin settings, explaining what each feature does and the impact of changing it.

## Table of Contents

- [Overview](#overview)
- [Quality Presets](#quality-presets)
- [DiT Engine Settings](#dit-engine-settings)
- [LLM Planner Settings](#llm-planner-settings)
- [Audio Processing Settings](#audio-processing-settings)
- [Backup & Restore](#backup--restore)
- [Troubleshooting](#troubleshooting)

---

## Overview

### How Settings Are Stored

Admin settings persist in your browser's localStorage under the key `signalHorizon.adminSettings`. This means:

- ✅ Settings survive page refreshes and browser restarts
- ✅ Each browser/profile has independent settings
- ❌ Settings do NOT sync across devices
- ❌ Clearing browser data will reset settings

### Settings Flow

```
Admin Settings → Merged with UI Input → API Request → Generation
```

When you click "Generate", Signal Horizon merges your visible UI choices (title, lyrics, BPM) with the hidden admin settings to form the complete request.

---

## Quality Presets

Quality presets provide one-click configurations for the most common use cases. These define the **Inference Steps** and **Guidance Scale** used during generation.

### Preset Definitions

| Preset | Steps | Guidance | Est. Time* | Best For |
|--------|:-----:|:--------:|:----------:|----------|
| ⚡ **Fast** | 16 | 5 | ~15s | Quick previews, rapid iteration |
| ⚖️ **Balanced** | 60 | 8 | ~45s | Daily production work |
| ✨ **Pro** | 100 | 9 | ~80s | High-quality output |
| 🔥 **Ultra** | 150 | 8 | ~120s | Final releases, maximum quality |

*Times are estimates for a 60-second track on an RTX 3080. Actual times vary by GPU and duration.

---

### Understanding Each Parameter

#### Inference Steps

**What it does:** Controls how many denoising passes the DiT model performs to generate audio.

| Value | Effect | Trade-off |
|-------|--------|-----------|
| 8-20 | Rough output, may have artifacts | Very fast |
| 40-60 | Good balance of quality and speed | Recommended for iteration |
| 80-100 | Detailed, polished output | Significantly slower |
| 120-200 | Maximum refinement | Diminishing returns past 100 |

> **Impact of Change:** Doubling steps roughly doubles generation time. Quality improvements become marginal above 100 steps for most content.

#### Guidance Scale

**What it does:** Controls how strictly the model follows your prompt versus allowing creative freedom.

| Value | Effect | Trade-off |
|-------|--------|-----------|
| 3-5 | Loose interpretation, more model creativity | May drift from your intent |
| 7-9 | Balanced adherence | Recommended default |
| 10-15 | Strict prompt following | May sound forced or unnatural |
| 15+ | Very literal interpretation | Risk of artifacts |

> **Impact of Change:** Higher values can cause "over-fitting" where output loses natural variation. Lower values may ignore parts of your prompt.

---

## DiT Engine Settings

The DiT (Diffusion Transformer) is the core audio synthesis model. These settings control how it generates audio from noise.

### Shift (Timestep Distribution)

| Setting | Default | Range |
|---------|:-------:|:-----:|
| Shift | 3.0 | 1.0 - 5.0 |

**What it does:** Determines how the model allocates its denoising effort across the generation process.

| Value | Behavior | Best For |
|-------|----------|----------|
| 1.0-2.0 | Even distribution, more detail work | Rich textures, complex arrangements |
| 3.0 | Balanced (recommended) | General use |
| 4.0-5.0 | Front-loaded structure, less detail | Clean, minimal productions |

> ⚠️ **Impact of Change:** Shift dramatically affects output character. Higher shift = clearer structure but potentially "drier" sound with less ornamentation.

### Inference Method

| Setting | Default | Options |
|---------|:-------:|:-------:|
| Inference Method | ODE | ODE, SDE |

**What it does:** Determines the mathematical approach to denoising.

| Method | Full Name | Behavior |
|--------|-----------|----------|
| **ODE** | Ordinary Differential Equation | Deterministic — same seed = identical result |
| **SDE** | Stochastic Differential Equation | Adds randomness during denoising |

> **Impact of Change:** SDE introduces variation even with the same seed, useful for exploring creative space. ODE is required for reproducible results.

### Use ADG (Adaptive Dual Guidance)

| Setting | Default | Options |
|---------|:-------:|:-------:|
| Use ADG | Off | On, Off |

**What it does:** Dynamically adjusts CFG (Classifier-Free Guidance) throughout the generation process.

| State | Effect |
|-------|--------|
| **Off** | Static guidance, faster generation |
| **On** | Adaptive guidance, better prompt adherence, ~30% slower |

> **Impact of Change:** ADG improves quality at the cost of speed. Most noticeable on complex prompts with multiple style requirements.

---

## LLM Planner Settings

The 5Hz LM (Language Model) acts as a "planner" that interprets your prompt and generates semantic codes for the DiT.

### Thinking Mode (Chain-of-Thought)

| Setting | Default | Options |
|---------|:-------:|:-------:|
| Thinking Mode | On | On, Off |

**What it does:** When enabled, the LLM reasons through metadata (BPM, key, structure) before generating codes.

| State | Effect |
|-------|--------|
| **On** | LLM infers optimal BPM, key, and song structure automatically |
| **Off** | Skips LLM reasoning, uses your exact inputs without inference |

> ⚠️ **CRITICAL:** Thinking Mode **MUST be OFF** when running in Dev Mode (`--skip-llm`). If enabled without an initialized LLM, generation will hang at 0%.

### LM CFG Scale

| Setting | Default | Range |
|---------|:-------:|:-----:|
| LM CFG Scale | 3.5 | 1.0 - 10.0 |

**What it does:** Controls how closely the language model follows your prompt.

| Value | Effect |
|-------|--------|
| 1.0-2.0 | Very loose, highly creative interpretations |
| 3.0-4.0 | Balanced (recommended) |
| 5.0+ | Strict adherence, may reduce musicality |

> **Impact of Change:** Lower values allow the LLM to "fill in blanks" creatively. Higher values force literal interpretation which can feel mechanical.

### LM Temperature

| Setting | Default | Range |
|---------|:-------:|:-----:|
| LM Temperature | 0.85 | 0.1 - 2.0 |

**What it does:** Controls randomness in the LLM's token sampling.

| Value | Effect |
|-------|--------|
| 0.1-0.5 | Deterministic, predictable output |
| 0.7-0.9 | Balanced creativity (recommended) |
| 1.0-1.5 | High creativity, may be inconsistent |
| 1.5+ | Very random, potential for unexpected results |

> **Impact of Change:** Higher temperature increases variation between generations with the same prompt. Use lower values when you want consistent, reproducible styles.

---

## Audio Processing Settings

These post-processing options ensure consistent, broadcast-ready audio output.

### Loudness Normalization

| Setting | Default | Options |
|---------|:-------:|:-------:|
| Loudness Normalization | On | On, Off |

**What it does:** Automatically adjusts output volume to a consistent LUFS (Loudness Units Full Scale) level.

| State | Effect |
|-------|--------|
| **On** | All tracks normalized to target LUFS — consistent playback volume |
| **Off** | Raw output — volume varies based on generation |

> **Impact of Change:** Turning this off may result in tracks that are too quiet or too loud compared to reference material.

### Target LUFS

| Setting | Default | Range |
|---------|:-------:|:-----:|
| Target LUFS | -14 | -24 to -8 |

**What it does:** Sets the target loudness level for normalization.

| Value | Platform/Use Case |
|-------|-------------------|
| -14 LUFS | **Spotify**, YouTube, general streaming |
| -16 LUFS | **Apple Music**, iTunes |
| -18 LUFS | Podcasts, audiobooks |
| -23 LUFS | Broadcast television (EBU R128) |

> **Impact of Change:** Using the wrong target may cause platforms to re-normalize your audio (potentially reducing dynamic range) or result in tracks that sound too loud/quiet relative to other content.

### Peak Limiter

| Setting | Default | Options |
|---------|:-------:|:-------:|
| Peak Limiter | On | On, Off |

**What it does:** Prevents audio peaks from exceeding 0 dB, which causes digital clipping (distortion).

| State | Effect |
|-------|--------|
| **On** | Loud peaks are limited — no clipping |
| **Off** | Peaks may exceed 0 dB — risk of audible distortion |

> **Impact of Change:** Turning this off may result in harsh distortion on loud sections. Keep it on unless you plan to master the audio yourself in a DAW.

---

## Backup & Restore

### Export Settings

Click **📤 Export Settings** to download a JSON file containing all your admin configurations. Use this to:

- Share your optimal settings with collaborators
- Back up before experimenting
- Move settings to a new browser or device

### Import Settings

Click **📥 Import Settings** and select a previously exported JSON file to restore all settings at once.

### Reset to Defaults

Click **🔄 Reset to Defaults** to restore factory settings. This is useful if:

- You've over-tuned and generations aren't producing good results
- You want a clean slate after experimenting
- You're troubleshooting unexpected behavior

---

## Troubleshooting

### Generation Hangs at 0%

**Symptom:** Progress bar stays at 0%, no audio generated.

**Likely Cause:** Thinking Mode is ON but LLM is not initialized.

**Solution:** 
1. If running Dev Mode: Disable Thinking Mode in Admin Settings
2. If not in Dev Mode: Restart server and ensure LLM loads successfully

---

### Inconsistent Volume Across Tracks

**Symptom:** Some tracks are very loud, others very quiet.

**Likely Cause:** Loudness Normalization is disabled.

**Solution:** Enable Loudness Normalization and set Target LUFS to -14.

---

### Output Sounds Robotic or Artificial

**Symptom:** Music follows prompt but sounds mechanical.

**Likely Cause:** LM CFG Scale too high OR Guidance Scale too high.

**Solution:** 
- Reduce LM CFG Scale to 3.0-3.5
- Reduce Guidance Scale to 7-8
- Increase LM Temperature slightly (0.85-0.95)

---

### Missing Detail or Flat Sound

**Symptom:** Audio lacks texture, sounds "demo-quality."

**Likely Cause:** Shift too high OR Steps too low.

**Solution:**
- Reduce Shift to 2.5-3.0
- Increase Steps to 80+
- Try SDE inference method for more variation

---

### Audio Distortion on Loud Parts

**Symptom:** Harsh clipping sound on peaks.

**Likely Cause:** Peak Limiter is disabled.

**Solution:** Enable Peak Limiter in Audio Processing settings.

---

## See Also

- [Gradio Interface Guide](GRADIO_GUIDE.md) – Full Gradio UI documentation
- [Tutorial](Tutorial.md) – Core concepts and model architecture
- [API Reference](API.md) – REST API documentation
