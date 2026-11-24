from fastapi import FastAPI
from app.config import settings
from app.database import engine, Base
from app import models
from app.routers import videos

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)

app.include_router(videos.router)


@app.get("/health")
def health_check():
    response_data = {}
    response_data["status"] = "ok"
    response_data["app"] = settings.app_name
    response_data["env"] = settings.app_env
    return response_data