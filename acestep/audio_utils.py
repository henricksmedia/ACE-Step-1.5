"""
Audio saving and transcoding utility module

Independent audio file operations outside of handler, supporting:
- Save audio tensor/numpy to files (default FLAC format, fast)
- Format conversion (FLAC/WAV/MP3)
- Batch processing
- Loudness normalization (LUFS-based)
- Peak limiting
"""

import os
import hashlib
import json
from pathlib import Path
from typing import Union, Optional, List, Tuple
import torch
import numpy as np
import torchaudio
from loguru import logger

# Optional dependency for loudness normalization
try:
    import pyloudnorm as pyln
    PYLOUDNORM_AVAILABLE = True
except ImportError:
    PYLOUDNORM_AVAILABLE = False
    logger.warning("pyloudnorm not installed. Loudness normalization disabled. Install with: pip install pyloudnorm")


# ============================================================================
# Loudness Normalization Functions
# ============================================================================

def normalize_loudness(
    audio_data: Union[torch.Tensor, np.ndarray],
    sample_rate: int = 48000,
    target_lufs: float = -14.0,
    channels_first: bool = True,
) -> np.ndarray:
    """
    Normalize audio to target LUFS (Loudness Units Full Scale).
    
    Industry standard targets:
    - Spotify/YouTube: -14 LUFS
    - Apple Music: -16 LUFS
    - Broadcast (EBU R128): -23 LUFS
    
    Args:
        audio_data: Audio tensor [channels, samples] or numpy array
        sample_rate: Audio sample rate
        target_lufs: Target loudness in LUFS (default -14.0)
        channels_first: If True, input is [channels, samples]
        
    Returns:
        Normalized audio as numpy array [channels, samples]
    """
    if not PYLOUDNORM_AVAILABLE:
        logger.warning("pyloudnorm not available, skipping loudness normalization")
        if isinstance(audio_data, torch.Tensor):
            return audio_data.cpu().numpy()
        return audio_data
    
    # Convert to numpy if needed
    if isinstance(audio_data, torch.Tensor):
        audio_np = audio_data.cpu().numpy()
    else:
        audio_np = audio_data.copy()
    
    # Ensure channels_first format [channels, samples]
    if not channels_first and audio_np.ndim == 2:
        audio_np = audio_np.T
    
    # pyloudnorm expects [samples, channels] format
    if audio_np.ndim == 2:
        audio_for_meter = audio_np.T  # [samples, channels]
    else:
        audio_for_meter = audio_np.reshape(-1, 1)  # mono to [samples, 1]
    
    try:
        # Create meter and measure current loudness
        meter = pyln.Meter(sample_rate)
        current_lufs = meter.integrated_loudness(audio_for_meter)
        
        # Skip if audio is silent or very quiet (avoid amplifying noise)
        if current_lufs < -70.0 or np.isinf(current_lufs):
            logger.debug(f"Audio too quiet ({current_lufs:.1f} LUFS), skipping normalization")
            return audio_np
        
        # Normalize to target
        normalized = pyln.normalize.loudness(audio_for_meter, current_lufs, target_lufs)
        
        # Convert back to channels_first [channels, samples]
        if normalized.ndim == 2:
            normalized = normalized.T
        else:
            normalized = normalized.flatten()
        
        logger.debug(f"[Loudness] Normalized {current_lufs:.1f} LUFS → {target_lufs:.1f} LUFS")
        return normalized
        
    except Exception as e:
        logger.warning(f"Loudness normalization failed: {e}, returning original audio")
        return audio_np


def apply_peak_limiter(
    audio_data: Union[torch.Tensor, np.ndarray],
    ceiling_db: float = -1.0,
    channels_first: bool = True,
) -> np.ndarray:
    """
    Apply a simple peak limiter to prevent clipping.
    
    Uses soft-knee limiting to reduce peaks above the ceiling.
    
    Args:
        audio_data: Audio tensor [channels, samples] or numpy array
        ceiling_db: Maximum peak level in dB (default -1.0 dBTP)
        channels_first: If True, input is [channels, samples]
        
    Returns:
        Limited audio as numpy array [channels, samples]
    """
    # Convert to numpy if needed
    if isinstance(audio_data, torch.Tensor):
        audio_np = audio_data.cpu().numpy()
    else:
        audio_np = audio_data.copy()
    
    # Calculate ceiling as linear value
    ceiling_linear = 10 ** (ceiling_db / 20.0)
    
    # Find current peak
    current_peak = np.max(np.abs(audio_np))
    
    if current_peak > ceiling_linear:
        # Apply simple gain reduction (true peak limiting would be more complex)
        reduction = ceiling_linear / current_peak
        audio_np = audio_np * reduction
        logger.debug(f"[Limiter] Reduced peak by {20 * np.log10(reduction):.1f} dB")
    
    return audio_np


def post_process_audio(
    audio_data: Union[torch.Tensor, np.ndarray],
    sample_rate: int = 48000,
    normalize: bool = True,
    target_lufs: float = -14.0,
    limit_peaks: bool = True,
    peak_ceiling_db: float = -1.0,
    channels_first: bool = True,
) -> np.ndarray:
    """
    Apply full post-processing chain: loudness normalization + peak limiting.
    
    This fixes both inter-track and intra-track volume fluctuation by:
    1. Normalizing to a consistent loudness target (LUFS)
    2. Limiting peaks to prevent clipping
    
    Args:
        audio_data: Audio tensor or numpy array
        sample_rate: Audio sample rate
        normalize: Whether to apply LUFS normalization
        target_lufs: Target loudness in LUFS
        limit_peaks: Whether to apply peak limiting
        peak_ceiling_db: Peak ceiling in dB
        channels_first: If True, input is [channels, samples]
        
    Returns:
        Processed audio as numpy array [channels, samples]
    """
    # Convert to numpy
    if isinstance(audio_data, torch.Tensor):
        audio_np = audio_data.cpu().numpy()
    else:
        audio_np = audio_data.copy()
    
    # Step 1: Loudness normalization (adjusts overall level)
    if normalize:
        audio_np = normalize_loudness(
            audio_np, 
            sample_rate=sample_rate, 
            target_lufs=target_lufs,
            channels_first=channels_first
        )
    
    # Step 2: Peak limiting (catches any transients that exceed ceiling)
    if limit_peaks:
        audio_np = apply_peak_limiter(
            audio_np,
            ceiling_db=peak_ceiling_db,
            channels_first=channels_first
        )
    
    return audio_np




class AudioSaver:
    """Audio saving and transcoding utility class"""
    
    def __init__(self, default_format: str = "flac"):
        """
        Initialize audio saver
        
        Args:
            default_format: Default save format ('flac', 'wav', 'mp3')
        """
        self.default_format = default_format.lower()
        if self.default_format not in ["flac", "wav", "mp3"]:
            logger.warning(f"Unsupported format {default_format}, using 'flac'")
            self.default_format = "flac"
    
    def save_audio(
        self,
        audio_data: Union[torch.Tensor, np.ndarray],
        output_path: Union[str, Path],
        sample_rate: int = 48000,
        format: Optional[str] = None,
        channels_first: bool = True,
    ) -> str:
        """
        Save audio data to file
        
        Args:
            audio_data: Audio data, torch.Tensor [channels, samples] or numpy.ndarray
            output_path: Output file path (extension can be omitted)
            sample_rate: Sample rate
            format: Audio format ('flac', 'wav', 'mp3'), defaults to default_format
            channels_first: If True, tensor format is [channels, samples], else [samples, channels]
        
        Returns:
            Actual saved file path
        """
        format = (format or self.default_format).lower()
        if format not in ["flac", "wav", "mp3"]:
            logger.warning(f"Unsupported format {format}, using {self.default_format}")
            format = self.default_format
        
        # Ensure output path has correct extension
        output_path = Path(output_path)
        if output_path.suffix.lower() not in ['.flac', '.wav', '.mp3']:
            output_path = output_path.with_suffix(f'.{format}')
        
        # Convert to torch tensor
        if isinstance(audio_data, np.ndarray):
            if channels_first:
                # numpy [samples, channels] -> tensor [channels, samples]
                audio_tensor = torch.from_numpy(audio_data.T).float()
            else:
                # numpy [samples, channels] -> tensor [samples, channels] -> [channels, samples]
                audio_tensor = torch.from_numpy(audio_data).float()
                if audio_tensor.dim() == 2 and audio_tensor.shape[0] < audio_tensor.shape[1]:
                    audio_tensor = audio_tensor.T
        else:
            # torch tensor
            audio_tensor = audio_data.cpu().float()
            if not channels_first and audio_tensor.dim() == 2:
                # [samples, channels] -> [channels, samples]
                if audio_tensor.shape[0] > audio_tensor.shape[1]:
                    audio_tensor = audio_tensor.T
        
        # Ensure memory is contiguous
        audio_tensor = audio_tensor.contiguous()
        
        # Select backend and save
        try:
            if format == "mp3":
                # MP3 uses ffmpeg backend
                torchaudio.save(
                    str(output_path),
                    audio_tensor,
                    sample_rate,
                    channels_first=True,
                    backend='ffmpeg',
                )
            elif format in ["flac", "wav"]:
                # FLAC and WAV use soundfile backend (fastest)
                torchaudio.save(
                    str(output_path),
                    audio_tensor,
                    sample_rate,
                    channels_first=True,
                    backend='soundfile',
                )
            else:
                # Other formats use default backend
                torchaudio.save(
                    str(output_path),
                    audio_tensor,
                    sample_rate,
                    channels_first=True,
                )
            
            logger.debug(f"[AudioSaver] Saved audio to {output_path} ({format}, {sample_rate}Hz)")
            return str(output_path)
            
        except Exception as e:
            try:
                import soundfile as sf
                audio_np = audio_tensor.transpose(0, 1).numpy()  # -> [samples, channels]
                sf.write(str(output_path), audio_np, sample_rate, format=format.upper())
                logger.debug(f"[AudioSaver] Fallback soundfile Saved audio to {output_path} ({format}, {sample_rate}Hz)")
                return str(output_path)
            except Exception as e:
                logger.error(f"[AudioSaver] Failed to save audio: {e}")
                raise
    
    def convert_audio(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        output_format: str,
        remove_input: bool = False,
    ) -> str:
        """
        Convert audio format
        
        Args:
            input_path: Input audio file path
            output_path: Output audio file path
            output_format: Target format ('flac', 'wav', 'mp3')
            remove_input: Whether to delete input file
        
        Returns:
            Output file path
        """
        input_path = Path(input_path)
        output_path = Path(output_path)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        # Load audio
        audio_tensor, sample_rate = torchaudio.load(str(input_path))
        
        # Save as new format
        output_path = self.save_audio(
            audio_tensor,
            output_path,
            sample_rate=sample_rate,
            format=output_format,
            channels_first=True
        )
        
        # Delete input file if needed
        if remove_input:
            input_path.unlink()
            logger.debug(f"[AudioSaver] Removed input file: {input_path}")
        
        return output_path
    
    def save_batch(
        self,
        audio_batch: Union[List[torch.Tensor], torch.Tensor],
        output_dir: Union[str, Path],
        file_prefix: str = "audio",
        sample_rate: int = 48000,
        format: Optional[str] = None,
        channels_first: bool = True,
    ) -> List[str]:
        """
        Save audio batch
        
        Args:
            audio_batch: Audio batch, List[tensor] or tensor [batch, channels, samples]
            output_dir: Output directory
            file_prefix: File prefix
            sample_rate: Sample rate
            format: Audio format
            channels_first: Tensor format flag
        
        Returns:
            List of saved file paths
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Process batch
        if isinstance(audio_batch, torch.Tensor) and audio_batch.dim() == 3:
            # [batch, channels, samples]
            audio_list = [audio_batch[i] for i in range(audio_batch.shape[0])]
        elif isinstance(audio_batch, list):
            audio_list = audio_batch
        else:
            audio_list = [audio_batch]
        
        saved_paths = []
        for i, audio in enumerate(audio_list):
            output_path = output_dir / f"{file_prefix}_{i:04d}"
            saved_path = self.save_audio(
                audio,
                output_path,
                sample_rate=sample_rate,
                format=format,
                channels_first=channels_first
            )
            saved_paths.append(saved_path)
        
        return saved_paths


def get_audio_file_hash(audio_file) -> str:
    """
    Get hash identifier for an audio file.
    
    Args:
        audio_file: Path to audio file (str) or file-like object
    
    Returns:
        Hash string or empty string
    """
    if audio_file is None:
        return ""
    
    try:
        if isinstance(audio_file, str):
            if os.path.exists(audio_file):
                with open(audio_file, 'rb') as f:
                    return hashlib.md5(f.read()).hexdigest()
            return hashlib.md5(audio_file.encode('utf-8')).hexdigest()
        elif hasattr(audio_file, 'name'):
            return hashlib.md5(str(audio_file.name).encode('utf-8')).hexdigest()
        return hashlib.md5(str(audio_file).encode('utf-8')).hexdigest()
    except Exception:
        return hashlib.md5(str(audio_file).encode('utf-8')).hexdigest()


def generate_uuid_from_params(params_dict) -> str:
    """
    Generate deterministic UUID from generation parameters.
    Same parameters will always generate the same UUID.
    
    Args:
        params_dict: Dictionary of parameters
    
    Returns:
        UUID string
    """
    
    params_json = json.dumps(params_dict, sort_keys=True, ensure_ascii=False)
    hash_obj = hashlib.sha256(params_json.encode('utf-8'))
    hash_hex = hash_obj.hexdigest()
    uuid_str = f"{hash_hex[0:8]}-{hash_hex[8:12]}-{hash_hex[12:16]}-{hash_hex[16:20]}-{hash_hex[20:32]}"
    return uuid_str


def generate_uuid_from_audio_data(
    audio_data: Union[torch.Tensor, np.ndarray],
    seed: Optional[int] = None
) -> str:
    """
    Generate UUID from audio data (for caching/deduplication)
    
    Args:
        audio_data: Audio data
        seed: Optional seed value
    
    Returns:
        UUID string
    """
    if isinstance(audio_data, torch.Tensor):
        # Convert to numpy and calculate hash
        audio_np = audio_data.cpu().numpy()
    else:
        audio_np = audio_data
    
    # Calculate data hash
    data_hash = hashlib.md5(audio_np.tobytes()).hexdigest()
    
    if seed is not None:
        combined = f"{data_hash}_{seed}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    return data_hash


# Global default instance
_default_saver = AudioSaver(default_format="flac")


def save_audio(
    audio_data: Union[torch.Tensor, np.ndarray],
    output_path: Union[str, Path],
    sample_rate: int = 48000,
    format: Optional[str] = None,
    channels_first: bool = True,
) -> str:
    """
    Convenience function: save audio (using default configuration)
    
    Args:
        audio_data: Audio data
        output_path: Output path
        sample_rate: Sample rate
        format: Format (default flac)
        channels_first: Tensor format flag
    
    Returns:
        Saved file path
    """
    return _default_saver.save_audio(
        audio_data, output_path, sample_rate, format, channels_first
    )

