from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Kelp AI Investment Teaser Platform",
    description="Automated M&A Teaser Generation",
    version="0.1.0"
)

origins = [
    "http://localhost:5173",  # Vite default port
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    from app.db import models
    from app.db.database import engine
    models.Base.metadata.create_all(bind=engine)

from app.api.api import api_router
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to Kelp AI Platform API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
