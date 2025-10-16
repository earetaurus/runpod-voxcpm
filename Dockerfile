FROM ghcr.io/earetaurus/vibevoiceapi:latest
WORKDIR /app
COPY runpod_voicedownloader.py .
ENV HF_HOME=/workspace/hf
ENV vibevoicemodel=vibevoice/VibeVoice-7B
ENV vibevoiceport=8000
ENV vibevoicewav=none
CMD ["python","runpod_voicedownloader.py","${vibevoicewav}"]
ENTRYPOINT ["python", "-m", "vibevoice_api.server", "--model_path", "${vibevoicemodel}", "--port", "${vibevoiceport}"]