from dotenv import load_dotenv
import os

load_dotenv()

MODELS_DIR = os.getenv("MODELS_DIR", "models/")
LLAMA_SERVER_PATH = os.getenv("LLAMA_SERVER_PATH", "llama.cpp/llama-server.exe")
LLAMA_SERVER_HOST = os.getenv("LLAMA_SERVER_HOST", "127.0.0.1")