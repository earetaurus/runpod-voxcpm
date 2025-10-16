FROM ghcr.io/earetaurus/vibevoiceapi:latest
WORKDIR /app
COPY rp-serverless.py .
ENV HF_HOME=/workspace/hf
ENV vibevoicemodel=vibevoice/VibeVoice-7B
ENV vibevoicewav=none
#CMD ["python","runpod_voicedownloader.py","${vibevoicewav}"]
#ENTRYPOINT ["python", "-m", "vibevoice_api.server", "--model_path", "${vibevoicemodel}", "--port", "${vibevoiceport}"]
ENTRYPOINT ["python","rp-serverless.py"]