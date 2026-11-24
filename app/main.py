from fastapi import FastAPI
from app.config import settings

app = FastAPI(title=settings.app_name)


@app.get("/health")
def health_check():
    response_data = {}
    response_data["status"] = "ok"
    response_data["app"] = settings.app_name
    response_data["env"] = settings.app_env
    return response_data