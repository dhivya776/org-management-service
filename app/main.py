from fastapi import FastAPI
from app.routes import router

app = FastAPI(title="Organization Management Service")

app.include_router(router)

@app.get("/")
def home():
    return {"message": "Service is running. Go to /docs for API testing."}