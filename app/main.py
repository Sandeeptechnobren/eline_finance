from fastapi import FastAPI
from app.api.query import router

app = FastAPI(title="Forecast Query Builder API")

app.include_router(router)
