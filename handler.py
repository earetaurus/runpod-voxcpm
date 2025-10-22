import base64
import io
import os

import numpy as np
import soundfile as sf
import torch
import torchaudio
import runpod
from voxcpm import VoxCPM
from transformers.trainer_utils import set_seed

# --- Env ---
VOXCPM_MODEL = os.getenv("VOXCPM_MODEL", "openbmb/VoxCPM-0.5B")
DEFAULT_LANGUAGE = os.getenv("LANGUAGE", "en") # VoxCPM might not use language codes directly, adjust as needed.
# HF_TOKEN is not directly used by VoxCPM in the same way as VibeVoice for model loading,
# but might be needed if the model is private. Assuming public for now.

# --- Device ---
device = "cuda" if torch.cuda.is_available() else "cpu"

# --- Load once at startup ---
print(f"[VoxCPM] Loading model '{VOXCPM_MODEL}' on {device}...")
# Initialize VoxCPM model
# Note: VoxCPM's generate and generate_streaming methods directly take text.
# Language parameter might need to be handled differently based on VoxCPM's capabilities
# or by ensuring the model is trained for the desired language.
model = VoxCPM.from_pretrained(VOXCPM_MODEL)

# Store sample rate from the model
SAMPLE_RATE = model.tts_model.sample_rate

def synthesize_speech(text: str,prompt_text: str = None,prompt_wav_path: str = None, language: str = None) -> str:
    """
    Generate speech audio from text using VoxCPM and return base64-encoded WAV.
    VoxCPM's generate_streaming returns chunks, which are concatenated.
    Language parameter is kept for signature compatibility but might not be used by VoxCPM.
    """
    audio_chunks = []
    for chunk in model.generate_streaming(text,prompt_wav_path,prompt_text):
        audio_chunks.append(chunk)

    if not audio_chunks:
        raise RuntimeError("VoxCPM did not return any audio chunks.")

    audio = np.concatenate(audio_chunks)

    # Ensure audio is in the expected format (e.g., float32)
    if audio.dtype != np.float32:
        audio = audio.astype(np.float32)

    buf = io.BytesIO()
    # Use soundfile to save the audio data
    sf.write(buf, audio, SAMPLE_RATE, format="wav")
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")

def handler(job):

    job_input = job.get("input", {})
    text = job_input.get("text")
    prompt_text = job_input.get('prompt_text', None)
    prompt_wav_url = job_input.get('prompt_wav_url', None)
    prompt_wav_path = None
    if prompt_wav_url:
        custom_wav_folder = "/workspace/customwav"
        os.makedirs(custom_wav_folder, exist_ok=True)
        # Create a filename from the URL or use a default if URL is just a domain
        filename = os.path.basename(prompt_wav_url)
        if not filename:
            filename = "downloaded_prompt.wav"
        prompt_wav_path = os.path.join(custom_wav_folder, filename)

    # Language might not be directly supported by VoxCPM in the same way as VibeVoice
    # We'll pass it but note it might be ignored by the model.
    language = job_input.get("language", DEFAULT_LANGUAGE)

    if not isinstance(text, str) or not text.strip():
        return {"error": "Missing required 'text' (non-empty string)."}

    try:
        # Pass language if it's meaningful for VoxCPM, otherwise omit or handle as None
        # For now, passing it as is, assuming it might be used in future versions or specific models.
        audio_b64 = synthesize_speech(text.strip(),prompt_text,prompt_wav_path, language)
        # Return the language code that was requested or default
        return {"language": language, "audio_base64": audio_b64}
    except Exception as e:
        # Let RunPod mark the job as FAILED and surface the exception details
        raise RuntimeError(f"Inference failed: {e}")

# Check if the script is run directly (for local testing or execution)
if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})

# This line is crucial for RunPod serverless execution
runpod.serverless.start({"handler": handler})
