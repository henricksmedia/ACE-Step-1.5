"""
Signal Horizon - Lightweight Launcher
Uses ACE-Step's built-in Gradio server with clean UI served on same port
"""
import os
import sys
from pathlib import Path

# Setup path
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent

# Add project to path
sys.path.insert(0, str(PROJECT_ROOT))

# Load environment
from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env", override=False)
load_dotenv(PROJECT_ROOT / ".env.example", override=False)

# Clear proxy settings
for proxy_var in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY']:
    os.environ.pop(proxy_var, None)


def main():
    import argparse
    import threading
    import webbrowser
    
    parser = argparse.ArgumentParser(description="Signal Horizon")
    parser.add_argument("--port", type=int, default=8372)  # SH in ASCII = 83+72
    parser.add_argument("--init_service", type=str, default="false")
    parser.add_argument("--skip_llm", type=str, default="false", help="Skip LLM loading for fast dev mode")
    parser.add_argument("--model", type=str, default="turbo", choices=["turbo", "base"],
                        help="Model to load: turbo (fast) or base (extract/lego/complete)")
    args = parser.parse_args()
    
    init_service = args.init_service.lower() == "true"
    skip_llm = args.skip_llm.lower() == "true"
    
    # Determine model config path
    model_config = "acestep-v15-base" if args.model == "base" else "acestep-v15-turbo"
    model_display = "Base (full features)" if args.model == "base" else "Turbo (fast)"
    
    print("\n" + "="*60)
    print("  ✧ SIGNAL HORIZON ✧")
    print("  AI-Powered Music Generation")
    print(f"  Model: {model_display}")
    print("="*60)
    
    # Import ACE-Step components
    import gradio as gr
    from fastapi import FastAPI
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse, HTMLResponse
    from fastapi.middleware.cors import CORSMiddleware
    
    from acestep.handler import AceStepHandler
    from acestep.llm_inference import LLMHandler
    from acestep.dataset_handler import DatasetHandler
    from acestep.gpu_config import get_gpu_config, print_gpu_config_info, set_global_gpu_config
    from acestep.gradio_ui.interfaces import create_gradio_interface
    from acestep.gradio_ui.api_routes import router as api_router, set_api_key
    
    # GPU config
    gpu_cfg = get_gpu_config()
    set_global_gpu_config(gpu_cfg)
    print_gpu_config_info(gpu_cfg)
    
    # Initialize handlers
    dit_handler = AceStepHandler()
    llm_handler = LLMHandler()
    dataset_handler = DatasetHandler()
    
    # Initialize models if requested
    if init_service:
        print(f"\nLoading {model_display} model...")
        dit_handler.initialize_service(
            project_root=str(PROJECT_ROOT),
            config_path=model_config,
            device="auto",
            use_flash_attention=False,
            offload_to_cpu=gpu_cfg.gpu_memory_gb < 16,
        )
        print("✓ DiT model loaded!")
        
        # Initialize LLM handler (skip in dev mode for fast startup)
        if skip_llm:
            print("⚡ DEV MODE: Skipping LLM initialization for fast startup")
            print("  (sample_mode and format features disabled)")
        else:
            checkpoint_dir = str(PROJECT_ROOT / "checkpoints")
            lm_model_path = "acestep-5Hz-lm-1.7B"
            
            print("Initializing LLM (this may take 80-90 seconds)...")
            status_msg, success = llm_handler.initialize(
                checkpoint_dir=checkpoint_dir,
                lm_model_path=lm_model_path,
                backend="vllm",
                device="auto",
                offload_to_cpu=gpu_cfg.gpu_memory_gb < 16,
            )
            if success:
                print("✓ LLM model loaded!")
            else:
                print(f"⚠ LLM initialization failed: {status_msg}")
        print()
    
    # Create FastAPI app
    app = FastAPI(title="Signal Horizon")
    
    # Add CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Store handlers
    app.state.dit_handler = dit_handler
    app.state.llm_handler = llm_handler
    
    # Mount API routes with /api prefix
    set_api_key(None)
    app.include_router(api_router, prefix="/api")
    
    # Serve clean UI at root
    @app.get("/", response_class=HTMLResponse)
    async def serve_ui():
        html_path = SCRIPT_DIR / "index.html"
        if html_path.exists():
            return FileResponse(html_path)
        return HTMLResponse("<h1>Signal Horizon</h1><p>index.html not found</p>")
    
    # Serve promo page
    @app.get("/promo.html", response_class=HTMLResponse)
    async def serve_promo():
        promo_path = SCRIPT_DIR / "promo.html"
        if promo_path.exists():
            return FileResponse(promo_path)
        return HTMLResponse("<h1>Promo Not Found</h1>")
    
    # Try to create Gradio interface for advanced features (optional)
    try:
        init_params = {'init_llm': False, 'device': 'auto'} if init_service else None
        demo = create_gradio_interface(
            dit_handler, llm_handler, dataset_handler,
            init_params=init_params, language='en'
        )
        # Mount Gradio at /gradio
        app = gr.mount_gradio_app(app, demo, path="/gradio")
        gradio_available = True
    except Exception as e:
        print(f"⚠️  Gradio interface disabled: {e}")
        gradio_available = False
    
    # Open browser after short delay
    def open_browser():
        import time
        time.sleep(2)
        webbrowser.open(f"http://127.0.0.1:{args.port}")
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    print(f"\n✧ Signal Horizon ready!")
    print(f"  Clean UI:    http://127.0.0.1:{args.port}/")
    if gradio_available:
        print(f"  Full UI:     http://127.0.0.1:{args.port}/gradio")
    print(f"  API:         http://127.0.0.1:{args.port}/api/")
    print()
    
    # Run server
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=args.port, log_level="warning")


if __name__ == "__main__":
    main()
