from abc import ABC, abstractmethod
from typing import Iterator


class ModelAdapter(ABC):
    @classmethod
    @abstractmethod
    def supports(csl, model_path: str) -> bool: ...

    @abstractmethod
    def load(self, model_path: str, **kwargs) -> None: ...

    @abstractmethod
    def generate(self, messages: list[dict], **kwargs) -> str: ...

    @abstractmethod
    def stream(self, messages: list[dict], **kwargs) -> Iterator[str]: ...

    @abstractmethod
    def unload(self) -> None: ...

    @abstractmethod
    def is_loaded(self) -> bool: ...

    @abstractmethod
    def count_tokens(self, text: str) -> int: ...