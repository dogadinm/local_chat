import subprocess
import time
import httpx
import json
import socket

from typing import Iterator
from backend.adapters.base import ModelAdapter


class LlamaCppServerAdapter(ModelAdapter):
    def __init__(self, port: int | None = None, host: str = "127.0.0.1"):
        self._process = None
        self._model_path = None
        self._host = host
        self._port = port if port is not None else self._find_free_port()
        self._server_url = f"http://{self._host}:{self._port}"

    @staticmethod
    def _find_free_port() -> int:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            return s.getsockname()[1]

    @classmethod
    def supports(cls, model_path: str) -> bool:
        return model_path.endswith(".gguf")

    def load(self, model_path: str, **kwargs) -> None:
        self._model_path = model_path
        cmd = [
            "llama.cpp/llama-server.exe",
            "--model",
            model_path,
            "--port",
            str(self._port),
            "--ctx-size",
            str(kwargs.get("ctx_size", 4096)),
            "--n-gpu-layers",
            str(kwargs.get("n_gpu_layers", 0)),
            "--threads",
            str(kwargs.get("threads", 4)),
            "--batch-size",
            str(kwargs.get("batch_size", 512)),
            "--parallel",
            str(kwargs.get("parallel", 1)),
        ]
        if kwargs.get("flash_attn", False):
            cmd.append("--flash-attn")
        self._process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        self._wait_ready()

    def _wait_ready(self, timeout: int = 60) -> None:
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                httpx.get(f"{self._server_url}/health", timeout=2)
                return
            except Exception:
                time.sleep(1)
        raise RuntimeError("llama-server did not start within the allotted time.")

    def generate(self, messages: list[dict], **kwargs) -> str:
        response = httpx.post(
            f"{self._server_url}/v1/chat/completions",
            json={"messages": messages, "stream": False, **kwargs},
            timeout=120,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    def stream(self, messages: list[dict], **kwargs) -> Iterator[str]:
        with httpx.stream(
            "POST",
            f"{self._server_url}/v1/chat/completions",
            json={"messages": messages, "stream": True, **kwargs},
            timeout=120,
        ) as response:
            for line in response.iter_lines():
                if line.startswith("data: ") and line != "data: [DONE]":
                    chunk = json.loads(line[6:])
                    delta = chunk["choices"][0]["delta"].get("content", "")
                    if delta:
                        yield delta

    def is_loaded(self) -> bool:
        return self._process is not None and self._process.poll() is None

    def count_tokens(self, text: str) -> int:
        response = httpx.post(
            f"{self._server_url}/tokenize",
            json={"content": text},
            timeout=10,
        )
        response.raise_for_status()
        return len(response.json()["tokens"])

    def unload(self) -> None:
        if self._process:
            self._process.terminate()
            self._process.wait()
            self._process = None
