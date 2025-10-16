FROM alpine:latest

WORKDIR /app
RUN apk add git build-base uv
RUN git clone https://github.com/earetaurus/VibeVoice-API
WORKDIR /app/VibeVoice-API
RUN uv venv --python 3.11
RUN uv pip install vibevoice-api prometheus_client

# ENV SOME_VARIABLE=some_value
EXPOSE 8000

# Command to run the application
CMD ["python", "-m", "vibevoice_api.server", "--model_path", "vibevoice/VibeVoice-7B", "--port", "8000"]