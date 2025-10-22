FROM python:3.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app
COPY requirements.txt .
COPY handler.py .
COPY qtest_predownload.py .
COPY .runpod ./.runpod
RUN apt update && apt install build-essential -y --no-install-recommends && rm -rf /var/lib/apt/lists/*
RUN uv pip install --no-cache-dir -r requirements.txt --system
ENV HF_HOME=/workspace/hf
ENV VOXCPM_MODEL=openbmb/VoxCPM-0.5B
RUN uv run qtest_predownload.py
#CMD ["python3", "-u", "handler.py"]
CMD ["uv", "run", "handler.py"]