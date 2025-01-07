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
from .routers import part_models, souq_scraper

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


headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
}
lc_100_url: str = "https://toyota-usa.epc-data.com/land_cruiser/uzj100l/3703/"


# @app.get("/epc/main-categories")
# async def scrape_main_categories() -> list[str]:
#     r = requests.get(url=lc_100_url, headers=headers)

#     soup = BeautifulSoup(r.content, "html5lib")

#     titles = soup.find_all("h3")

#     main_cats = []
#     for title in titles:
#         main_cats.append(title.contents[0].string)
#     return main_cats[:-1]


# @app.get("/epc/main-category")
# async def scrape_main_category(main_category: MainCategoryUrls) -> list[Category]:
#     r = requests.get(url=lc_100_url + main_category, headers=headers)

#     soup = BeautifulSoup(r.content, "html5lib")

#     tables = soup.find_all("td", "detail_list")

#     body_categories: list[Category] = []
#     for table in tables:
#         idx = 0
#         cat: Category = {"number": "", "title": ""}
#         for desc in table.descendants:
#             if idx == 0 and isinstance(desc, str):
#                 cat["number"] = desc[0:-3].replace("/n", "").strip()
#                 idx += 1
#             elif idx == 1:
#                 idx += 1
#             elif idx == 2:
#                 cat["title"] = desc
#                 idx += 1
#             elif idx > 2:
#                 idx = 0
#                 if cat["title"] != "Go to top":
#                     body_categories.append(cat)
#                 cat = {"number": "", "title": ""}

#     return body_categories


# @app.post("/epc/categories")
# async def scrape_categories(
#     main_category: MainCategoryUrls,
#     categories: CategoryReq,
# ) -> list[Part]:
#     parts = []
#     for category in categories.cats[0:2]:
#         ext = category.number.replace("-", "").strip()
#         # if number < full length, it's a category

#         r = requests.get(url=lc_100_url + main_category + ext + "/", headers=headers)
#         soup = BeautifulSoup(r.content, "html5lib")
#         tables = soup.find_all("td", "detail_list")

#         for table in tables:
#             for desc in table.find_all("a"):
#                 link_url = desc["href"]
#                 name = desc.text.strip()

#                 splitted = link_url.split("/")
#                 parts.append(
#                     {"number": splitted[-2], "category": splitted[-4], "title": name}
#                 )

#     return parts


# app.include_router(parts.router)
app.include_router(souq_scraper.router)
app.include_router(part_models.router)


main_cats = [
    "Engine, fuel system and tools",
    "Transmission and chassis",
    "Body and interior",
    "Electrics",
]

body_and_interior_cats = [
    {"number": "51-51", "title": "FRAME"},
    {"number": "51-52", "title": "SUSPENSION CROSSMEMBER & UNDER COVER"},
    {"number": "52-51", "title": "CAB MOUNTING & BODY MOUNTING"},
    {"number": "52-52", "title": "FRONT BUMPER & BUMPER STAY"},
    {"number": "53-51", "title": "RADIATOR GRILLE"},
    {"number": "53-53", "title": "HOOD & FRONT FENDER"},
    {"number": "53-54", "title": "HOOD LOCK & HINGE"},
    {"number": "53-55", "title": "FRONT FENDER APRON & DASH PANEL"},
    {"number": "55-53", "title": "COWL PANEL & WINDSHIELD GLASS"},
    {"number": "58-53", "title": "FLOOR INSULATOR"},
    {"number": "61-51", "title": "SIDE MEMBER"},
    {"number": "67-51", "title": "FRONT DOOR PANEL & GLASS"},
    {"number": "67-53", "title": "FRONT DOOR LOCK & HANDLE"},
    {"number": "67-55", "title": "REAR DOOR PANEL & GLASS"},
    {"number": "67-56", "title": "REAR DOOR LOCK & HANDLE"},
    {"number": "67-65", "title": "LOCK CYLINDER SET"},
    {"number": "74-51", "title": "ARMREST & VISOR"},
    {"number": "74-54", "title": "BATTERY CARRIER"},
    {"number": "74-55", "title": "CAUTION PLATE"},
    {"number": "75-51", "title": "EMBLEM & NAME PLATE"},
    {"number": "75-52", "title": "MOULDING"},
    {"number": "75-53", "title": "BODY STRIPE"},
    {"number": "77-51", "title": "FUEL TANK & TUBE"},
    {"number": "51-53", "title": "SPARE WHEEL CARRIER"},
    {"number": "52-53", "title": "REAR BUMPER & BUMPER STAY"},
    {"number": "55-51", "title": "INSTRUMENT PANEL & GLOVE COMPARTMENT"},
    {"number": "58-51", "title": "FRONT FLOOR PANEL & FRONT FLOOR MEMBER"},
    {"number": "58-52", "title": "REAR FLOOR PANEL & REAR FLOOR MEMBER"},
    {"number": "58-54", "title": "FLOOR MAT & SILENCER PAD"},
    {"number": "58-55", "title": "CONSOLE BOX & BRACKET"},
    {"number": "61-52", "title": "SIDE WINDOW"},
    {"number": "61-53", "title": "ROOF PANEL & BACK PANEL"},
    {"number": "61-55", "title": "REAR VENTILATOR & ROOF VENTILATOR"},
    {"number": "64-51", "title": "INSIDE TRIM BOARD"},
    {"number": "64-52", "title": "ROOF HEADLINING & SILENCER PAD"},
    {"number": "64-54", "title": "PACKAGE TRAY PANEL"},
    {"number": "67-54", "title": "FRONT DOOR WINDOW REGULATOR & HINGE"},
    {"number": "67-57", "title": "REAR DOOR WINDOW REGULATOR & HINGE"},
    {"number": "67-61", "title": "BACK DOOR PANEL & GLASS"},
    {"number": "67-62", "title": "BACK DOOR LOCK & HINGE"},
    {"number": "71-51", "title": "SEAT & SEAT TRACK"},
    {"number": "71-52", "title": "SEAT BELT"},
    {"number": "74-56", "title": "ASH RECEPTACLE"},
    {"number": "75-54", "title": "TOOL BOX & LICENSE PLATE BRACKET"},
    {"number": "76-52", "title": "SPOILER & SIDE MUDGUARD"},
    {"number": "78-51", "title": "ACCELERATOR LINK"},
]

engine_fuel_system_tools_cats = [
    {"number": "09-01", "title": "STANDARD TOOL"},
    {"number": "11-01", "title": "PARTIAL ENGINE ASSEMBLY"},
    {"number": "11-02", "title": "SHORT BLOCK ASSEMBLY"},
    {"number": "11-03", "title": "ENGINE OVERHAUL GASKET KIT"},
    {"number": "11-04", "title": "CYLINDER HEAD"},
    {"number": "11-05", "title": "CYLINDER BLOCK"},
    {"number": "11-06", "title": "TIMING GEAR COVER & REAR END PLATE"},
    {"number": "11-07", "title": "MOUNTING"},
    {"number": "12-01", "title": "VENTILATION HOSE"},
    {"number": "13-01", "title": "CRANKSHAFT & PISTON"},
    {"number": "13-02", "title": "CAMSHAFT & VALVE"},
    {"number": "15-01", "title": "OIL PUMP"},
    {"number": "15-02", "title": "OIL FILTER"},
    {"number": "15-03", "title": "OIL COOLER"},
    {"number": "16-01", "title": "WATER PUMP"},
    {"number": "16-03", "title": "RADIATOR & WATER OUTLET"},
    {"number": "16-05", "title": "V-BELT"},
    {"number": "17-01", "title": "MANIFOLD"},
    {"number": "17-02", "title": "EXHAUST PIPE"},
    {"number": "17-03", "title": "AIR CLEANER"},
    {"number": "17-06", "title": "MANIFOLD AIR INJECTION SYSTEM"},
    {"number": "17-08", "title": "VACUUM PIPING"},
    {"number": "17-09", "title": "CAUTION PLATE & NAME PLATE"},
    {"number": "19-01", "title": "IGNITION COIL & SPARK PLUG"},
    {"number": "19-03", "title": "ALTERNATOR"},
    {"number": "19-04", "title": "STARTER"},
    {"number": "22-11", "title": "FUEL INJECTION SYSTEM"},
]

chassis_cats = [
    {"number": "33-12", "title": "SHIFT LEVER & RETAINER"},
    {"number": "35-01", "title": "TRANSAXLE OR TRANSMISSION ASSY & GASKET KIT (ATM)"},
    {"number": "35-02", "title": "TORQUE CONVERTER, FRONT OIL PUMP & CHAIN (ATM)"},
    {"number": "35-03", "title": "TRANSMISSION CASE & OIL PAN (ATM)"},
    {"number": "35-04", "title": "EXTENSION HOUSING (ATM)"},
    {"number": "35-05", "title": "SPEEDOMETER DRIVEN GEAR (ATM)"},
    {"number": "35-06", "title": "OVERDRIVE GEAR (ATM)"},
    {"number": "35-07", "title": "BRAKE BAND & MULTIPLE DISC CLUTCH (ATM)"},
    {"number": "35-08", "title": "CENTER SUPPORT & PLANETARY SUN GEAR (ATM)"},
    {"number": "35-09", "title": "BRAKE NO.3, 1ST & REVERSE BRAKE (ATM)"},
    {"number": "35-10", "title": "PLANETARY GEAR, REVERSE PISTON & COUNTER GEAR(ATM)"},
    {"number": "35-12", "title": "VALVE BODY & OIL STRAINER (ATM)"},
    {"number": "35-13", "title": "THROTTLE LINK & VALVE LEVER (ATM)"},
    {"number": "35-14", "title": "OIL COOLER & TUBE (ATM)"},
    {"number": "36-08", "title": "TRANSFER ASSEMBLY & GASKET KIT"},
    {"number": "36-09", "title": "TRANSFER CASE & EXTENSION HOUSING"},
    {"number": "36-10", "title": "TRANSFER GEAR"},
    {"number": "36-11", "title": "TRANSFER LEVER & SHIFT ROD"},
    {"number": "37-01", "title": "PROPELLER SHAFT & UNIVERSAL JOINT"},
    {"number": "41-01", "title": "REAR AXLE HOUSING & DIFFERENTIAL"},
    {"number": "41-02", "title": "REAR AXLE SHAFT & HUB"},
    {"number": "41-03", "title": "DISC WHEEL & WHEEL CAP"},
    {"number": "43-01", "title": "FRONT AXLE HOUSING & DIFFERENTIAL"},
    {"number": "43-02", "title": "FRONT DRIVE SHAFT"},
    {"number": "43-03", "title": "FRONT AXLE HUB"},
    {"number": "45-01", "title": "STEERING COLUMN & SHAFT"},
    {"number": "45-02", "title": "VANE PUMP & RESERVOIR (POWER STEERING PUMP)"},
    {"number": "45-03", "title": "POWER STEERING TUBE"},
    {"number": "45-04", "title": "STEERING WHEEL"},
    {"number": "45-05", "title": "FRONT STEERING GEAR & LINK"},
    {"number": "46-01", "title": "PARKING BRAKE & CABLE"},
    {"number": "47-01", "title": "BRAKE PEDAL & BRACKET"},
    {"number": "47-02", "title": "BRAKE MASTER CYLINDER"},
    {"number": "47-05", "title": "FRONT DISC BRAKE CALIPER & DUST COVER"},
    {"number": "47-07", "title": "REAR DISC BRAKE CALIPER & DUST COVER"},
    {"number": "47-08", "title": "BRAKE TUBE & CLAMP"},
    {"number": "48-02", "title": "FRONT AXLE ARM & STEERING KNUCKLE"},
    {"number": "48-03", "title": "FRONT SPRING & SHOCK ABSORBER"},
    {"number": "48-04", "title": "REAR SPRING & SHOCK ABSORBER"},
    {"number": "48-05", "title": "HEIGHT CONTROL (AUTO-LEVELER)"},
]

electric_cats = [
    {"number": "81-01", "title": "HEADLAMP"},
    {"number": "81-02", "title": "FOG LAMP"},
    {"number": "81-03", "title": "FRONT TURN SIGNAL LAMP"},
    {"number": "81-11", "title": "REAR COMBINATION LAMP"},
    {"number": "81-13", "title": "REAR LICENSE PLATE LAMP"},
    {"number": "81-15", "title": "REFLEX REFLECTOR"},
    {"number": "81-17", "title": "CENTER STOP LAMP"},
    {"number": "81-21", "title": "INTERIOR LAMP"},
    {"number": "85-01", "title": "WINDSHIELD WIPER"},
    {"number": "85-02", "title": "REAR WIPER"},
    {"number": "85-03", "title": "WINDSHIELD WASHER"},
    {"number": "85-04", "title": "REAR WASHER"},
    {"number": "86-04", "title": "ANTENNA"},
    {"number": "86-11", "title": "HORN"},
    {"number": "87-01", "title": "MIRROR"},
    {"number": "82-01", "title": "BATTERY & BATTERY CABLE"},
    {"number": "82-02", "title": "WIRING & CLAMP"},
    {"number": "83-01", "title": "METER"},
    {"number": "83-02", "title": "INDICATOR"},
    {"number": "84-01", "title": "SWITCH & RELAY"},
    {"number": "84-04", "title": "ELECTRONIC FUEL INJECTION SYSTEM"},
    {"number": "84-08", "title": "CRUISE CONTROL (AUTO DRIVE)"},
    {"number": "84-10", "title": "OVERDRIVE & ELECTRONIC CONTROLLED TRANSMISSION"},
    {"number": "84-14", "title": "ABS & VSC"},
    {"number": "84-16", "title": "AUTOMATIC LIGHT CONTROL SYSTEM (CONLIGHT)"},
    {"number": "84-19", "title": "ELECTRONIC MODULATED SUSPENSION"},
    {"number": "84-20", "title": "WIRELESS DOOR LOCK"},
    {"number": "84-21", "title": "AIR BAG"},
    {"number": "84-23", "title": "ACTIVE CONTROL SUSPENSION (ELECTRICAL PARTS)"},
    {"number": "84-24", "title": "ANTI-THEFT DEVICE"},
    {"number": "84-35", "title": "TIRE PRESSURE WARNING SYSTEM"},
    {"number": "85-11", "title": "DOOR MOTOR & DOOR SOLENOID"},
    {"number": "85-13", "title": "SEAT MOTOR & SEAT HEATER"},
    {"number": "86-01", "title": "RADIO & TAPE PLAYER"},
    {"number": "86-02", "title": "SPEAKER"},
    {"number": "86-03", "title": "MULTI-DISPLAY (CRT DISPLAY)"},
    {"number": "86-06", "title": "TELEVISION & CAMERA"},
    {"number": "87-12", "title": "HEATING & AIR CONDITIONING - HEATER UNIT & BLOWER"},
    {"number": "87-14", "title": "HEATING & AIR CONDITIONING - COOLER UNIT"},
    {"number": "87-15", "title": "HEATING & AIR CONDITIONING - CONTROL & AIR DUCT"},
    {"number": "87-16", "title": "HEATING & AIR CONDITIONING - WATER PIPING"},
    {"number": "87-18", "title": "HEATING & AIR CONDITIONING - COOLER PIPING"},
    {"number": "87-19", "title": "HEATING & AIR CONDITIONING - COMPRESSOR"},
]
