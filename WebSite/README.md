# Systemix Website

Production-oriented FastAPI website for Systemix, an AI-driven business automation company.

## Run locally

1. Create a virtual environment.
2. Install dependencies with `pip install -r requirements.txt`.
3. Copy `.env.example` to `.env` if you want to customize runtime settings.
4. Start the server with `uvicorn app.main:app --reload`.
5. Open `http://127.0.0.1:8000`.

## Run with Docker

1. Optionally copy `.env.example` to `.env` if you want to override defaults.
2. Build and start the container with `docker compose up --build`.
3. Open `http://127.0.0.1:8000`.

To stop the stack, run `docker compose down`.
