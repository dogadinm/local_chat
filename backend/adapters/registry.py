import importlib
import pkgutil
from backend.adapters.base import ModelAdapter


class ModelRegistry:
    def __init__(self):
        self._adapters: list[type[ModelAdapter]] = []
        self._loaded: dict[str, ModelAdapter] = {}

    def register(self, adapter_cls: type[ModelAdapter]) -> None:
        if adapter_cls not in self._adapters:
            self._adapters.append(adapter_cls)

    def auto_discover(self) -> None:
        import backend.adapters as pkg

        for _, name, _ in pkgutil.iter_modules(pkg.__path__):
            if name in ("base", "registry"):
                continue
            module = importlib.import_module(f"backend.adapters.{name}")
            for attr in vars(module).values():
                if (
                    isinstance(attr, type)
                    and issubclass(attr, ModelAdapter)
                    and attr is not ModelAdapter
                ):
                    self.register(attr)

    def get(self, model_path: str) -> ModelAdapter:
        if model_path not in self._loaded:
            for adapter_cls in self._adapters:
                if adapter_cls.supports(model_path):
                    adapter = adapter_cls()
                    adapter.load(model_path)
                    self._loaded[model_path] = adapter
                    break
            else:
                raise ValueError(f"No adapter found for: {model_path}")
        return self._loaded[model_path]

    def list_loaded(self) -> list[str]:
        return list(self._loaded.keys())

    def unload(self, model_path: str) -> None:
        if model_path in self._loaded:
            self._loaded[model_path].unload()
            del self._loaded[model_path]


registry = ModelRegistry()
