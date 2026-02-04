# Audio Quality Guide

This guide covers audio quality optimization and troubleshooting for Signal Horizon.

---

## Volume Fluctuation Fix

### The Problem

AI-generated music can exhibit volume fluctuation in two forms:

1. **Inter-track fluctuation**: Different tracks have different loudness levels
2. **Intra-track fluctuation**: Volume "pumping" or "breathing" within a single track

### Root Causes

| Cause | Effect | Fix |
|-------|--------|-----|
| Low inference steps | Unstable waveform amplitude | Increase to 32+ steps |
| Shift factor mismatch | Denoising trajectory issues | Use shift=3.0 for turbo models |
| No loudness normalization | Raw model output varies | Enable LUFS normalization |

---

## Recommended Settings for Stable Output

### Quick Reference

| Preset | Steps | Shift | Description |
|--------|-------|-------|-------------|
| Fast | 32 | 3.0 | Quick preview, stable |
| Balanced | 80 | 3.0 | Best quality/speed ratio |
| Pro | 100 | 3.0 | High quality |
| Ultra | 150 | 3.0 | Maximum quality |

> **Key insight**: Steps below 32 can cause volume fluctuation. The turbo model was trained with shift=3.0, so always use that value.

---

## Loudness Normalization

Signal Horizon includes automatic loudness normalization using the LUFS standard.

### What is LUFS?

LUFS (Loudness Units Full Scale) is the industry standard for measuring perceived loudness:

| Platform | Target LUFS |
|----------|-------------|
| Spotify/YouTube | -14 LUFS |
| Apple Music | -16 LUFS |
| Broadcast (EBU R128) | -23 LUFS |

### Enabling Normalization

In **Admin Settings → Audio Processing**:

- **Loudness Normalization**: On (recommended)
- **Target LUFS**: -14 (default, matches streaming platforms)
- **Peak Limiter**: On (prevents clipping)

### Installing the Dependency

Loudness normalization requires `pyloudnorm`:

```bash
pip install pyloudnorm
```

If not installed, normalization is automatically skipped with a warning.

---

## Post-Processing Tips

For professional-quality output, apply these mastering steps in your DAW:

1. **Sub-Bass Cleanup**: High-pass filter at 30Hz
2. **Mud Removal**: Narrow cut at 200-400Hz if needed
3. **Air & Shimmer**: +2dB boost above 12kHz
4. **Final Limiting**: -1dB ceiling for loudness

---

## Troubleshooting

### Symptoms and Solutions

| Symptom | Likely Cause | Solution |
|---------|--------------|----------|
| Volume "pumping" | Low inference steps | Increase steps to 60+ |
| Tracks vary in loudness | No normalization | Enable LUFS normalization |
| Audio clips/distorts | Peak limiter off | Enable peak limiter |
| Quiet sections too loud | Over-normalization | Lower target LUFS to -16 |

### Checking Current Loudness

The terminal logs show normalization activity:

```
[Loudness] Normalized -18.2 LUFS → -14.0 LUFS
[Limiter] Reduced peak by -2.3 dB
```
