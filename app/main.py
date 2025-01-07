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


from enum import Enum

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# pip3 install seleniumbase
from .routers import souq_scraper

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


@app.get("/")
async def hello_world() -> str:
    return "Hello World"


class MainCategoryUrls(str, Enum):
    body = "body/"
    engine = "engine/"
    chassis = "chassis/"
    electric = "electric/"


main_cats = [
    "Engine, fuel system and tools",
    "Transmission and chassis",
    "Body and interior",
    "Electrics",
]


headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
}
lc_100_url: str = "https://toyota-usa.epc-data.com/land_cruiser/uzj100l/3703/"


# app.include_router(parts.router)
app.include_router(souq_scraper.router)
# app.include_router(part_models.router)
