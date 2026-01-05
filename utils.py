import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

def get_llm_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    return OpenAI(api_key=api_key)

def format_audit_log(entries):
    if not entries:
        return "No audit entries"
    log_lines = []
    for entry in entries:
        timestamp = entry.get("timestamp", "")
        level = entry.get("level", "INFO")
        message = entry.get("message", "")
        log_lines.append(f"[{timestamp}] {level}: {message}")
    return "\n".join(log_lines)

