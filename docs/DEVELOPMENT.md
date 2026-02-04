# Development Guide

## Hot Reload Development (Recommended)

Signal Horizon supports **hot reload development** where models stay loaded in memory while you iterate on code.

### Starting Development Mode

```bash
# Run the dev batch file
Signal Horizon (Dev).bat
```

Or manually:
```bash
uv run python signal-horizon/model_server.py --reload --port 8372
```

### How It Works

1. **First launch:** Models load once (~2-3 minutes)
2. **After loading:** Edit any file in `signal-horizon/`
3. **Auto-refresh:** Server detects changes and reloads routes
4. **Models persist:** No 2-3 minute wait on each code change!

### What Gets Hot-Reloaded

| Component | Hot Reload? | Notes |
|-----------|-------------|-------|
| `index.html` | ✅ Yes | Refresh browser to see changes |
| Python routes | ✅ Yes | Auto-detects, just refresh browser |
| API endpoints | ✅ Yes | Changes apply immediately |
| Model code | ❌ No | Requires full restart |

### Development Workflow

```
1. Start: Signal Horizon (Dev).bat
2. Wait for "Models ready!" message
3. Open http://127.0.0.1:8372
4. Edit code → Save → Refresh browser
5. Repeat step 4 as needed
```

## Project Files

### Core Files

| File | Purpose |
|------|---------|
| `index.html` | Main UI - edit for frontend changes |
| `model_server.py` | Hot-reload server with persistent models |
| `launcher.py` | Production launcher with Gradio integration |
| `server.py` | Standalone FastAPI server |

### Batch Files

| File | Mode | Models |
|------|------|--------|
| `Signal Horizon (Dev).bat` | Hot reload | Persist in memory |
| `Signal Horizon.bat` | Production | Load fresh |
| `Signal Horizon (Full).bat` | Full Gradio | Load fresh |

## Port Configuration

**Standard port:** `8372` (SH in ASCII)

All launchers default to this port. Override with `--port`:
```bash
uv run python signal-horizon/model_server.py --port 9000
```

## Troubleshooting

### Models taking too long to load

The LLM takes 80-90 seconds to initialize the tokenizer. This is a known upstream issue with ACE-Step. Use hot-reload mode to avoid repeated loads.

### Port already in use

```bash
# Find process using the port
netstat -ano | findstr :8372

# Kill the process
taskkill /PID <pid> /F
```

### Changes not appearing

1. Make sure you saved the file
2. Check the terminal for reload messages
3. Hard refresh browser: `Ctrl+Shift+R`
