"""
Signal Horizon - Custom AI Music Generation Tool
Built on ACE-Step 1.5
"""
import os
import sys

# Add ACE-Step to Python path  
ACESTEP_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ACESTEP_PATH)

# Load environment variables
from dotenv import load_dotenv
load_dotenv(os.path.join(ACESTEP_PATH, ".env"), override=False)
load_dotenv(os.path.join(ACESTEP_PATH, ".env.example"), override=False)

# Clear proxy settings
for proxy_var in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY']:
    os.environ.pop(proxy_var, None)

import gradio as gr
from acestep.handler import AceStepHandler
from acestep.llm_inference import LLMHandler
from acestep.dataset_handler import DatasetHandler
from acestep.gpu_config import get_gpu_config, print_gpu_config_info, set_global_gpu_config
from acestep.gradio_ui.interfaces.generation import create_generation_section
from acestep.gradio_ui.interfaces.result import create_results_section
from acestep.gradio_ui.interfaces.dataset import create_dataset_section
from acestep.gradio_ui.events import setup_event_handlers
from acestep.gradio_ui.i18n import get_i18n, t

# Signal Horizon Theme
SIGNAL_HORIZON_CSS = """
/* Signal Horizon Dark Theme */
:root {
    --sh-bg-base: #0a0a0a;
    --sh-bg-surface: #141414;
    --sh-bg-card: #1a1a1a;
    --sh-accent: #00d4ff;
    --sh-accent-glow: rgba(0, 212, 255, 0.4);
    --sh-text: #ffffff;
    --sh-text-muted: #888888;
    --sh-border: #2a2a2a;
}

body, .gradio-container {
    background: var(--sh-bg-base) !important;
}

.main-header {
    text-align: center;
    margin-bottom: 1.5rem;
    padding: 1rem;
}

.main-header h1 {
    font-family: 'Segoe UI', sans-serif;
    font-size: 2.5rem;
    font-weight: 300;
    color: var(--sh-accent) !important;
    text-shadow: 0 0 30px var(--sh-accent-glow);
    margin-bottom: 0.5rem;
    letter-spacing: 2px;
}

.main-header p {
    color: var(--sh-text-muted);
    font-size: 1rem;
}

/* Cards and panels */
.gr-box, .gr-panel, .gr-form {
    background: var(--sh-bg-card) !important;
    border: 1px solid var(--sh-border) !important;
    border-radius: 12px !important;
}

/* Primary button styling */
.gr-button-primary {
    background: linear-gradient(135deg, var(--sh-accent), #0099cc) !important;
    border: none !important;
    color: #000 !important;
    font-weight: 600 !important;
    box-shadow: 0 0 20px var(--sh-accent-glow) !important;
    transition: all 0.3s ease !important;
}

.gr-button-primary:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 0 30px var(--sh-accent-glow) !important;
}

/* Input fields */
.gr-input, .gr-textarea, .gr-dropdown {
    background: var(--sh-bg-surface) !important;
    border: 1px solid var(--sh-border) !important;
    color: var(--sh-text) !important;
}

.gr-input:focus, .gr-textarea:focus {
    border-color: var(--sh-accent) !important;
    box-shadow: 0 0 10px var(--sh-accent-glow) !important;
}

/* Labels */
label, .gr-label {
    color: var(--sh-text) !important;
}

/* Tabs */
.tabs .tab-nav button {
    color: var(--sh-text-muted) !important;
    border-bottom: 2px solid transparent !important;
}

.tabs .tab-nav button.selected {
    color: var(--sh-accent) !important;
    border-bottom: 2px solid var(--sh-accent) !important;
}

/* Slider */
.gr-slider input[type="range"] {
    accent-color: var(--sh-accent);
}

/* Checkbox */
.gr-checkbox input:checked {
    background: var(--sh-accent) !important;
}

/* Preset pills */
.preset-pill {
    display: inline-block;
    padding: 8px 16px;
    margin: 4px;
    background: var(--sh-bg-surface);
    border: 1px solid var(--sh-border);
    border-radius: 20px;
    color: var(--sh-text);
    cursor: pointer;
    transition: all 0.2s ease;
}

.preset-pill:hover {
    border-color: var(--sh-accent);
    box-shadow: 0 0 10px var(--sh-accent-glow);
}

.preset-pill.active {
    background: var(--sh-accent);
    color: #000;
}

/* Audio player */
audio {
    width: 100%;
    border-radius: 8px;
}

/* Accordion */
.gr-accordion {
    background: var(--sh-bg-card) !important;
    border: 1px solid var(--sh-border) !important;
}
"""

# Genre presets
GENRE_PRESETS = {
    "Top 100": {
        "Summer Pop Anthem": "upbeat pop, catchy hooks, bright synths, dance rhythm, radio-friendly, 120 BPM",
        "Viral TikTok": "trending sound, catchy melody, modern pop production, energetic, 128 BPM",
    },
    "Pop": {
        "Dance Pop": "dance pop, synth hooks, four-on-the-floor, euphoric chorus, 124 BPM",
        "Synth Pop": "80s inspired synth pop, analog synthesizers, retro vibes, 118 BPM",
        "Indie Pop": "indie pop, dreamy vocals, jangly guitars, lo-fi aesthetic, 110 BPM",
    },
    "Country": {
        "Nashville Storyteller": "country ballad, acoustic guitar, pedal steel, heartfelt lyrics, 96 BPM",
        "Modern Country": "contemporary country, pop influences, arena rock elements, 120 BPM",
        "Country Rock": "southern rock, driving guitars, country twang, 130 BPM",
    },
    "EDM": {
        "Festival Banger": "big room house, massive drops, festival anthem, euphoric, 128 BPM",
        "Deep House Session": "deep house, groovy bassline, smooth pads, underground vibe, 122 BPM",
        "Progressive Trance": "progressive trance, building arpeggios, emotional melodies, 138 BPM",
        "Orbital Classic": "orbital style progressive electronic, hypnotic synth arpeggios, pulsing bassline, four-on-the-floor kicks, atmospheric pads, acid 303 synth, 90s rave, 135 BPM",
    },
    "Hip-Hop": {
        "Trap Soul": "trap soul, smooth 808s, atmospheric pads, melodic, 140 BPM",
        "Boom Bap": "classic hip-hop, vinyl samples, hard drums, old school, 90 BPM",
        "Drill": "UK drill, sliding 808s, dark atmosphere, aggressive, 140 BPM",
    },
    "Rock": {
        "Classic Rock Riff": "classic rock, guitar riffs, powerful drums, stadium anthem, 120 BPM",
        "Indie Rock": "indie rock, jangly guitars, raw production, alternative vibes, 128 BPM",
        "Metal": "heavy metal, distorted guitars, double bass drums, aggressive, 160 BPM",
    },
    "R&B": {
        "Smooth R&B": "smooth r&b, silky vocals, jazz chords, sensual groove, 85 BPM",
        "Neo-Soul": "neo-soul, organic instruments, warm production, soulful, 95 BPM",
    },
    "Jazz": {
        "Smooth Jazz": "smooth jazz, saxophone lead, electric piano, relaxing, 100 BPM",
        "Lo-Fi Jazz": "lo-fi jazz, vinyl crackle, mellow piano, chill vibes, 75 BPM",
    },
    "Latin": {
        "Reggaeton": "reggaeton, dembow rhythm, urban latin, party vibes, 95 BPM",
        "Latin Pop": "latin pop, tropical influences, romantic, danceable, 110 BPM",
    },
    "Indie": {
        "Bedroom Pop": "bedroom pop, intimate production, dreamy reverb, lo-fi, 105 BPM",
        "Shoegaze": "shoegaze, wall of sound guitars, ethereal vocals, atmospheric, 115 BPM",
    }
}


def create_signal_horizon_interface(dit_handler, llm_handler, dataset_handler, init_params=None):
    """Create the Signal Horizon custom interface"""
    
    i18n = get_i18n('en')
    
    with gr.Blocks(
        title="Signal Horizon",
        theme=gr.themes.Base(
            primary_hue=gr.themes.colors.cyan,
            secondary_hue=gr.themes.colors.blue,
            neutral_hue=gr.themes.colors.gray,
        ).set(
            body_background_fill="#0a0a0a",
            body_background_fill_dark="#0a0a0a",
            block_background_fill="#1a1a1a",
            block_background_fill_dark="#1a1a1a",
            input_background_fill="#141414",
            input_background_fill_dark="#141414",
            button_primary_background_fill="#00d4ff",
            button_primary_background_fill_dark="#00d4ff",
            button_primary_text_color="#000000",
        ),
        css=SIGNAL_HORIZON_CSS
    ) as demo:
        
        # Header
        gr.HTML("""
        <div class="main-header">
            <h1>✧ SIGNAL HORIZON ✧</h1>
            <p>AI-Powered Music Generation • Built on ACE-Step 1.5</p>
        </div>
        """)
        
        # Quick Presets Section
        with gr.Accordion("🎨 Quick Presets", open=True):
            with gr.Row():
                genre_dropdown = gr.Dropdown(
                    choices=list(GENRE_PRESETS.keys()),
                    value="EDM",
                    label="Genre",
                    interactive=True
                )
                preset_dropdown = gr.Dropdown(
                    choices=list(GENRE_PRESETS["EDM"].keys()),
                    value="Orbital Classic",
                    label="Preset",
                    interactive=True
                )
                apply_preset_btn = gr.Button("⚡ Apply Preset", variant="primary")
        
        # Main Generation Interface (from ACE-Step)
        generation_section = create_generation_section(dit_handler, llm_handler, init_params=init_params, language='en')
        
        # Results Section
        results_section = create_results_section(dit_handler)
        
        # Dataset section (hidden but required for event handlers)
        with gr.Accordion("📁 Dataset Explorer", open=False, visible=False):
            dataset_section = create_dataset_section(dataset_handler)
        
        # Setup event handlers from ACE-Step
        setup_event_handlers(demo, dit_handler, llm_handler, dataset_handler, 
                           dataset_section, generation_section, results_section)
        
        # Preset event handlers
        def update_presets(genre):
            return gr.Dropdown(choices=list(GENRE_PRESETS.get(genre, {}).keys()))
        
        def apply_preset(genre, preset):
            caption = GENRE_PRESETS.get(genre, {}).get(preset, "")
            return caption
        
        genre_dropdown.change(
            fn=update_presets,
            inputs=[genre_dropdown],
            outputs=[preset_dropdown]
        )
        
        # Connect apply preset to caption field (need to find the component)
        # This will be connected in a future update
        
    return demo


def main():
    """Main entry point for Signal Horizon"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Signal Horizon - AI Music Generation")
    parser.add_argument("--port", type=int, default=8372, help="Server port (SH in ASCII)")
    parser.add_argument("--server-name", type=str, default="127.0.0.1", help="Server address")
    parser.add_argument("--share", action="store_true", help="Create public link")
    parser.add_argument("--init_service", type=bool, default=False, help="Auto-initialize models")
    
    args = parser.parse_args()
    
    # Print GPU info
    gpu_cfg = get_gpu_config()
    set_global_gpu_config(gpu_cfg)
    print_gpu_config_info(gpu_cfg)
    
    # Initialize handlers
    dit_handler = AceStepHandler()
    llm_handler = LLMHandler()
    dataset_handler = DatasetHandler()
    
    # Prepare init params if requested
    init_params = None
    if args.init_service:
        init_params = {
            'init_llm': False,
            'device': 'auto',
        }
        print("\n" + "="*60)
        print("Initializing Signal Horizon...")
        print("="*60)
        dit_handler.initialize_service(
            project_root=ACESTEP_PATH,
            config_path="acestep-v15-turbo",
            device="auto",
            use_flash_attention=False,
            offload_to_cpu=gpu_cfg.gpu_memory_gb < 16,
        )
        print("✓ DiT model loaded!")
        
        # Initialize LLM handler
        checkpoint_dir = os.path.join(ACESTEP_PATH, "checkpoints")
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
        print("Service initialization completed!")
    
    # Create and launch interface
    print("\nLaunching Signal Horizon...")
    demo = create_signal_horizon_interface(dit_handler, llm_handler, dataset_handler, init_params)
    
    demo.queue()
    demo.launch(
        server_name=args.server_name,
        server_port=args.port,
        share=args.share,
        show_error=True
    )


if __name__ == "__main__":
    main()
