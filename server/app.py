from fastapi import FastAPI
from dotenv import load_dotenv
from backend.adapters.registry import registry
from server.routes import router

load_dotenv()

app = FastAPI()
app.include_router(router)


@app.on_event("startup")
async def startup():
    registry.auto_discover()