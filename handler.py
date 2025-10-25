import base64
import io
import os
import requests

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

def split_text_chunks(text: str, max_length: int = 1400) -> list:
    """
    Split text into chunks that don't exceed the maximum character limit.
    Tries to split at sentence boundaries when possible.
    """
    if len(text) <= max_length:
        return [text]
    
    chunks = []
    remaining_text = text
    
    while remaining_text:
        if len(remaining_text) <= max_length:
            chunks.append(remaining_text)
            break
        
        # Try to find a good breaking point (sentence end)
        # Look for periods, exclamation marks, or question marks followed by space or end
        break_point = max_length
        for i in range(max_length - 1, max(0, max_length - 200), -1):
            if i < len(remaining_text) and remaining_text[i] in '.!?':
                # Check if there's a space after or if it's the end
                if i == len(remaining_text) - 1 or (i + 1 < len(remaining_text) and remaining_text[i + 1] == ' '):
                    break_point = i + 1
                    break
        
        # If no good sentence break found, try to break at a space
        if break_point == max_length:
            for i in range(max_length - 1, max(0, max_length - 100), -1):
                if remaining_text[i] == ' ':
                    break_point = i
                    break
        
        # Extract the chunk
        chunk = remaining_text[:break_point].strip()
        if chunk:
            chunks.append(chunk)
        
        # Remove the processed part and any leading spaces
        remaining_text = remaining_text[break_point:].lstrip()
    
    return chunks


def synthesize_speech(text: str, prompt_text: str = None, prompt_wav_path: str = None, language: str = None) -> str:
    """
    Generate speech audio from text using VoxCPM and return base64-encoded WAV.
    Handles text splitting for inputs exceeding 1500 characters.
    VoxCPM's generate_streaming returns chunks, which are concatenated.
    Language parameter is kept for signature compatibility but might not be used by VoxCPM.
    """
    # Split text into chunks if it exceeds the character limit
    text_chunks = split_text_chunks(text, max_length=1400)
    
    all_audio_chunks = []
    
    for i, chunk in enumerate(text_chunks):
        print(f"[VoxCPM] Processing chunk {i+1}/{len(text_chunks)} ({len(chunk)} characters)")
        
        current_prompt_text = prompt_text
        
        chunk_audio_chunks = []
        for chunk_audio in model.generate_streaming(chunk, prompt_wav_path, current_prompt_text):
            chunk_audio_chunks.append(chunk_audio)
        
        if not chunk_audio_chunks:
            raise RuntimeError(f"VoxCPM did not return any audio chunks for chunk {i+1}.")
        
        all_audio_chunks.extend(chunk_audio_chunks)

    if not all_audio_chunks:
        raise RuntimeError("VoxCPM did not return any audio chunks.")

    audio = np.concatenate(all_audio_chunks)

    # Ensure audio is in the expected format (e.g., float32)
    if audio.dtype != np.float32:
        audio = audio.astype(np.float32)

    buf = io.BytesIO()
    # Use soundfile to save the audio data
    sf.write(buf, audio, SAMPLE_RATE, format="wav")
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


def download_wav(url: str, save_path: str):
    """Downloads a WAV file from a URL and saves it to a specified path."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an exception for bad status codes
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Successfully downloaded WAV from {url} to {save_path}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading WAV from {url}: {e}")
        raise


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
        # Download the WAV file if prompt_wav_url is provided
        download_wav(prompt_wav_url, prompt_wav_path)

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
