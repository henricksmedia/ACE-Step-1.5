"""
Signal Horizon - Clean UI Server
Serves the clean HTML UI and proxies to ACE-Step backend
"""
import os
import sys
from pathlib import Path

# Add ACE-Step to path
SCRIPT_DIR = Path(__file__).parent
ACESTEP_PATH = SCRIPT_DIR.parent
sys.path.insert(0, str(ACESTEP_PATH))

# Setup environment
from dotenv import load_dotenv
load_dotenv(ACESTEP_PATH / ".env", override=False)
load_dotenv(ACESTEP_PATH / ".env.example", override=False)

for proxy_var in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY']:
    os.environ.pop(proxy_var, None)

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from acestep.handler import AceStepHandler
from acestep.llm_inference import LLMHandler
from acestep.gpu_config import get_gpu_config, print_gpu_config_info, set_global_gpu_config
from acestep.gradio_ui.api_routes import router as api_router, set_api_key


# =============================================================================
# Singleton Model Holder - models load ONCE and persist across hot reloads
# =============================================================================
class ModelHolder:
    """Singleton to hold models across uvicorn reloads"""
    _instance = None
    dit_handler = None
    llm_handler = None
    initialized = False
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def initialize(self, skip_llm=False):
        if self.initialized:
            print("✓ Models already loaded (reusing from previous run)")
            return
            
        print("\n" + "="*60)
        print("  SIGNAL HORIZON")
        print("  AI-Powered Music Generation")
        print("="*60 + "\n")
        
        gpu_cfg = get_gpu_config()
        set_global_gpu_config(gpu_cfg)
        print_gpu_config_info(gpu_cfg)
        
        self.dit_handler = AceStepHandler()
        self.llm_handler = LLMHandler()
        
        # Initialize DiT service
        print("\nInitializing AI models...")
        self.dit_handler.initialize_service(
            project_root=str(ACESTEP_PATH),
            config_path="acestep-v15-turbo",
            device="auto",
            use_flash_attention=False,
            offload_to_cpu=gpu_cfg.gpu_memory_gb < 16,
        )
        print("✓ DiT model loaded!")
        
        if not skip_llm:
            # Initialize LLM handler
            checkpoint_dir = str(ACESTEP_PATH / "checkpoints")
            lm_model_path = "acestep-5Hz-lm-1.7B"
            
            print("Initializing LLM (this may take 80-90 seconds)...")
            status_msg, success = self.llm_handler.initialize(
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
        else:
            print("⚡ LLM skipped (dev mode)")
        
        print()
        self.initialized = True


# Initialize models at module load time (persists across reloads)
_model_holder = ModelHolder.get_instance()


def create_app(skip_llm=False):
    """Create FastAPI app - models are loaded via singleton"""
    
    # Ensure models are initialized
    _model_holder.initialize(skip_llm=skip_llm)
    
    app = FastAPI(title="Signal Horizon")
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Store handlers in app state
    app.state.dit_handler = _model_holder.dit_handler
    app.state.llm_handler = _model_holder.llm_handler
    
    # Mount API routes with /api prefix
    set_api_key(None)  # No auth required
    app.include_router(api_router, prefix="/api")
    
    # Serve static files
    app.mount("/static", StaticFiles(directory=str(SCRIPT_DIR)), name="static")
    
    # Serve index.html at root
    @app.get("/")
    async def serve_ui():
        return FileResponse(SCRIPT_DIR / "index.html")
    
    print("✧ Signal Horizon is ready!")
    return app


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Signal Horizon Server")
    parser.add_argument("--port", type=int, default=8372, help="Server port")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Server host")
    parser.add_argument("--skip-llm", action="store_true", help="Skip LLM loading for faster startup")
    args = parser.parse_args()
    
    app = create_app(skip_llm=args.skip_llm)
    
    print(f"  Open: http://{args.host}:{args.port}\n")
    
    uvicorn.run(app, host=args.host, port=args.port, log_level="warning")


if __name__ == "__main__":
    main()
