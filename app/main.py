# VIRTUAL ENVIRONMENT
# Start VE: source .venv/bin/activate
# Deactivate VE: deactivate
# Check if VE running: pip -V

# PACKAGE MANAGEMENT
# Install package: pip install "fastapi[standard]"
# Install all packages: pip install -r requirements.txt
# Update requirements.txt: pip freeze > requirements.txt

# FAST API
# Run server: fastapi dev main.py
# localhost: http://127.0.0.1:8000
# api docs: http://127.0.0.1:8000/docs
# alt api docs: http://127.0.0.1:8000/redoc
# JSON schema: http://127.0.0.1:8000/openapi.json


from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.models as models
from app.db import engine

from .routers import diagrams, groups, souq_scraper, souq_scraper_v2


@asynccontextmanager
async def lifespan(app: FastAPI):
    # create DB and tables
    models.Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="LC 100 Series UZJ100L-GNPEKA",
    description="LC 100 part groups, diagrams, and parts from PartsSouq",
    version="0.1",
    lifespan=lifespan,
)


origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def hello_world() -> str:
    return "Hello World"


app.include_router(groups.router)
app.include_router(diagrams.router)
app.include_router(souq_scraper.router)
app.include_router(souq_scraper_v2.router)
