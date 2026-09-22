"""
Configuration for the Proof-First Personal Agent.
Loads from environment variables and ~/.openclaw/secrets/nebius.env.
"""

import os
from pathlib import Path


def _load_key_from_env_file() -> str:
    secret_file = Path.home() / ".openclaw" / "secrets" / "nebius.env"
    if secret_file.exists():
        with secret_file.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("NEBIUS_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def load_config() -> dict:
    return {
        "nebius_api_key": os.getenv("NEBIUS_API_KEY", _load_key_from_env_file()),
        "model_id": os.getenv("MODEL_ID", "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B"),
        "memory_dir": os.getenv("MEMORY_DIR", str(Path.home() / ".nebius-hackathon" / "memory")),
        "base_url": os.getenv("BASE_URL", "https://api.tokenfactory.nebius.com/v1"),
        "timeout": int(os.getenv("API_TIMEOUT", "60")),
        "max_retries": int(os.getenv("API_MAX_RETRIES", "3")),
    }


config = load_config()
