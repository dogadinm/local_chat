from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from backend.adapters.registry import ModelRegistry
from backend.pipeline import Pipeline
from backend.config import MODELS_DIR
from server.state import get_registry
import os
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1")


class ChatRequest(BaseModel):
    model: str
    messages: list[dict]
    stream: bool = False


@router.get("/models")
def list_models():
    files = [f for f in os.listdir(MODELS_DIR) if f.endswith(".gguf")]
    return {"models": files}


@router.post("/chat/completions")
def chat(request: ChatRequest, registry: ModelRegistry = Depends(get_registry)):
    model_path = os.path.join(MODELS_DIR, request.model)
    logger.info(f"Chat request: model={request.model}, stream={request.stream}, messages={request.messages}")
    if not os.path.exists(model_path):
        raise HTTPException(status_code=404, detail=f"Model not found: {request.model}")

    logger.info(f"Loading adapter for: {model_path}")
    pipeline = Pipeline(registry.get(model_path))
    logger.info(f"Adapter ready, generating response")

    if request.stream:

        def generator():
            for chunk in pipeline.stream(request.messages):
                yield f"data: {json.dumps({'choices': [{'delta': {'content': chunk}}]})}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(generator(), media_type="text/event-stream")

    return {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": pipeline.run(request.messages),
                }
            }
        ]
    }
