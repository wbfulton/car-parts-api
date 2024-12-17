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


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import part_models, parts

app = FastAPI()

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
# get all parts
# get a part
# create a part
# update a part
# delete a part

# get a model
# get all models
# create a model
# update a model
# delete a model

# get all parts for a model
# add a part for a model
# delete a part for a model

# get all models for a part


# https://toyota.epc-data.com/land_cruiser/uzj100w/162888/


@app.get("/")
async def hello_world() -> str:
    return "Hello World"


app.include_router(parts.router)
app.include_router(part_models.router)
