from fastapi import Request
from backend.adapters.registry import ModelRegistry
from backend.pipeline import Pipeline


def get_registry(request: Request) -> ModelRegistry:
    return request.app.state.registry


def get_pipeline(model_path: str, request: Request) -> Pipeline:
    return Pipeline(request.app.state.registry.get(model_path))
