from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
