from typing import Iterator
from backend.adapters.base import ModelAdapter


class Pipeline:
    def __init__(self, adapter: ModelAdapter):
        self._adapter = adapter

    def run(self, messages: list[dict], **kwargs) -> str:
        return self._adapter.generate(messages, **kwargs)

    def stream(self, messages: list[dict], **kwargs) -> Iterator[str]:
        return self._adapter.stream(messages, **kwargs)
