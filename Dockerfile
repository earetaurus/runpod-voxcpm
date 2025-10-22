FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
COPY handler.py .
COPY .runpod ./.runpod
RUN pip install --no-cache-dir -r requirements.txt
ENV HF_HOME=/workspace/hf
ENV VOXCPM_MODEL=openbmb/VoxCPM-0.5B
ENV voxcpmwav=none
CMD ["python3", "-u", "handler.py"]