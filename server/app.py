from contextlib import asynccontextmanager
from fastapi import FastAPI
from dotenv import load_dotenv
from backend.adapters.registry import registry
from server.routes import router

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    registry.auto_discover()
    app.state.registry = registry
    yield
    for model_path in registry.list_loaded():
        registry.unload(model_path)


app = FastAPI(lifespan=lifespan)
app.include_router(router)
