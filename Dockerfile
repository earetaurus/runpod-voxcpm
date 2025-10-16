# Builder stage
FROM ghcr.io/astral-sh/uv:alpine as builder

WORKDIR /app
RUN apk add git build-base
# Clone the repository
RUN git clone https://github.com/vibevoice-community/VibeVoice-API.git
WORKDIR /app/VibeVoice-API

# Install the package using uv pip
RUN uv venv --python 3.11
RUN uv pip install -e . 

# --- Runner stage ---
FROM python:3.11-alpine

WORKDIR /app

# Copy installed packages from the builder stage
COPY --from=builder /app/VibeVoice-API/. /app/VibeVoice-API/
COPY --from=builder /app/.venv /app/.venv

# Set environment variables if needed
# ENV SOME_VARIABLE=some_value

# Expose the port the application runs on (if applicable)
EXPOSE 8000

# Command to run the application
CMD ["uv", "run", "-m", "vibevoice_api.server", "--model_path", "vibevoice/VibeVoice-7B", "--port", "8000"]