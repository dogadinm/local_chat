from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from backend.adapters.registry import registry
from backend.pipeline import Pipeline
import os
import json

router = APIRouter(prefix="/v1")


class ChatRequest(BaseModel):
    model: str
    messages: list[dict]
    stream: bool = False


@router.get("/models")
def list_models():
    models_dir = os.getenv("MODELS_DIR", "models/")
    files = [f for f in os.listdir(models_dir) if f.endswith(".gguf")]
    return {"models": files}


@router.post("/chat/completions")
def chat(request: ChatRequest):
    model_path = os.path.join(os.getenv("MODELS_DIR", "models/"), request.model)
    if not os.path.exists(model_path):
        raise HTTPException(status_code=404, detail=f"Model not found: {request.model}")

    adapter = registry.get(model_path)
    pipeline = Pipeline(adapter)

    if request.stream:
        def generator():
            for chunk in pipeline.stream(request.messages):
                yield f"data: {json.dumps({'choices': [{'delta': {'content': chunk}}]})}\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(generator(), media_type="text/event-stream")

    return {"choices": [{"message": {"role": "assistant", "content": pipeline.run(request.messages)}}]}