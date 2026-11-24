import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.database import engine, Base
from app import models
from app.routers import videos
from app.routers import ads
from app.storage import get_media_root

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)

app.include_router(videos.router)
app.include_router(ads.router)


@app.get("/health")
def health_check():
    response_data = {}
    response_data["status"] = "ok"
    response_data["app"] = settings.app_name
    response_data["env"] = settings.app_env
    return response_data


media_dir = get_media_root()
app.mount("/media", StaticFiles(directory=media_dir), name="media")

current_file_dir = os.path.dirname(os.path.abspath(__file__))
project_root_dir = os.path.dirname(current_file_dir)
frontend_dir = os.path.join(project_root_dir, "frontend")

if os.path.isdir(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")