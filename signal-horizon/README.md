# Signal Horizon

**AI-Powered Music Generation** • Built on ACE-Step 1.5

Signal Horizon is a streamlined interface for AI music generation, providing a clean UI on top of the powerful ACE-Step engine.

## ✨ Features

- **Clean Modern UI** - Minimalist interface for quick music generation
- **Full ACE-Step Power** - Access to DiT + LLM hybrid architecture
- **Hot Reload Development** - Edit code without reloading models
- **GPU Optimized** - Tier-based configuration for RTX 4070 Super and similar

## 🚀 Quick Start

### First Time Setup

```bash
# Clone ACE-Step 1.5 (if not already done)
git clone https://github.com/ace-step/ACE-Step-1.5.git

# Install dependencies via uv
uv sync
```

### Running Signal Horizon

| Batch File | Purpose | Use Case |
|------------|---------|----------|
| `Signal Horizon.bat` | Standard launch | Normal use |
| `Signal Horizon (Dev).bat` | Hot reload mode | Development |
| `Signal Horizon (Full).bat` | Full Gradio UI | Advanced features |

**Default URL:** `http://127.0.0.1:8372`

> **Port 8372** = 'SH' in ASCII (S=83, H=72) - unique and memorable!

## 📁 Project Structure

```
ACE-Step-1.5/
├── signal-horizon/           # Signal Horizon custom UI
│   ├── index.html           # Clean web interface
│   ├── launcher.py          # Production launcher
│   ├── model_server.py      # Hot-reload model server
│   └── server.py            # Standalone FastAPI server
├── acestep/                  # ACE-Step core engine
├── checkpoints/              # Model weights
└── docs/                     # Documentation
```

## 🛠️ Development

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for the development workflow.

**Key concept:** Use hot-reload mode to iterate quickly without reloading models (saves 2-3 minutes per restart).

## 📚 Documentation

- [Development Guide](docs/DEVELOPMENT.md) - Setting up for development
- [Architecture](docs/ARCHITECTURE.md) - How Signal Horizon works
- [API Reference](docs/API.md) - REST API endpoints

## 🎵 Usage

1. Launch Signal Horizon
2. Enter a music description (e.g., "upbeat electronic, 128 BPM")
3. Optionally add lyrics
4. Click Generate
5. Download your AI-generated music!

## 📄 License

Built on ACE-Step 1.5. See ACE-Step license for terms.
