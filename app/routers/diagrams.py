from typing import List, Tuple

from bs4 import BeautifulSoup
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import app.crud as crud
import app.schemas as schemas
from app.db import get_db
from app.routers.souq_scraper_v2 import (
    scrape_group_diagrams,
    scrape_save_group_diagrams,
)
from app.routers.utils import build_url

path_tag = "/diagrams"


router = APIRouter(
    prefix=path_tag,
    tags=[path_tag],
)


@router.get("/", response_model=List[schemas.Diagram])
async def get_all_diagrams(db: Session = Depends(get_db)):
    diagrams = crud.get_diagrams(db)

    return diagrams


@router.post("/scrape", response_model=List[schemas.CreateDiagram])
async def scrape_all_diagrams(
    db: Session = Depends(get_db), page_length: int = 435, token: int = 0
):
    groups = crud.get_groups_flat(db, page_length=400)

    valid_groups: list[schemas.Group] = []
    for group in groups:
        if group.diagrams_url is not None:
            valid_groups.append(group)

    diagrams: list[schemas.CreateDiagram] = []
    parts: list[schemas.CreatePart] = []
    for valid_group in valid_groups:
        [new_diagrams, new_parts] = await scrape_group_diagrams(valid_group)
        diagrams.extend(new_diagrams)
        parts.extend(new_parts)

    crud.post_bulk_diagrams(db, diagrams)
    crud.post_bulk_parts(db, parts)

    return diagrams


@router.post("/scrape/url", response_model=List[schemas.PartsSouqPageData])
async def scrape_all_diagram_urls(db: Session = Depends(get_db)):
    groups = crud.get_groups_flat(db, page_length=400)

    # 358 total
    valid_groups: list[schemas.Group] = []
    for group in groups:
        if group.diagrams_url is not None:
            urls = crud.get_group_url_html(db, group.id)
            if len(urls) == 0:
                valid_groups.append(group)

    for valid_group in valid_groups:
        [url, soup_str] = await scrape_save_group_diagrams(valid_group)
        crud.post_html_url(
            db,
            schemas.CreatePartsSouqPageData(
                id=valid_group.id, url=url, html_string=soup_str
            ),
        )

    return []


# ensure each group has a diagram
@router.post("/clean", response_model=List[schemas.CreateDiagram])
async def clean_all_diagrams(db: Session = Depends(get_db)):
    groups: list[schemas.Group] = crud.get_groups_flat(db, page_length=400)

    diagram_groups: list[schemas.Group] = []
    for group in groups:
        if group.diagrams_url is not None:
            diagram_groups.append(group)

    diagrams: list[schemas.CreateDiagram] = []
    parts: list[schemas.CreatePart] = []

    for i, diagram_group in enumerate(diagram_groups):
        html = crud.get_group_url_html(db, diagram_group.id)
        if html is not None:
            [new_diagrams, new_parts] = await parse_group_html(
                diagram_group, html.html_string
            )
            diagrams.extend(new_diagrams)
            parts.extend(new_parts)
            print(i, len(diagram_groups), diagram_group.id, len(diagrams), len(parts))

    crud.post_bulk_diagrams(db, diagrams)
    crud.post_bulk_parts(db, parts)

    return diagrams


async def parse_group_html(
    souq_group: schemas.Group, html: str
) -> Tuple[list[schemas.CreateDiagram], list[schemas.Part]]:
    if isinstance(souq_group, dict):
        souq_group = schemas.Group(**souq_group)

    soup = BeautifulSoup(html, "html5lib")

    diagram_panels = soup.find_all("div", class_="panel panel-default")
    diagrams: list[schemas.CreateDiagram] = []
    parts: list[schemas.CreatePart] = []

    for i, panel in enumerate(diagram_panels):
        header, body = panel.contents
        diagram_title = header.find("h2").text.strip()

        content_section = body.contents[0]
        parts_table, diagram_image = content_section.contents

        image_url = build_url(diagram_image.find("img")["src"])

        diagram_id = int(f"{souq_group.id}{i}")

        # Parse parts
        parts_rows = parts_table.find("tbody").contents

        for j, row in enumerate(parts_rows):
            number, name, part_code, note, amount, date_range = row.contents
            amount = amount.text.strip()
            while amount is not None and len(amount) > 1 and amount[0] == "0":
                amount = amount[1:]
            if amount == "" or amount == "X" or amount == "x":
                amount = None
            else:
                amount = int(amount)
            number = str(number.text.strip())
            part = {
                "name": str(name.text.strip()),
                "parent_diagram_id": diagram_id,
                "number": number,
                "note": note.text.strip(),
                "amount": amount,
                "date_range": date_range.text.strip(),
            }

            parts.append(
                schemas.CreatePart(
                    name=part["name"],
                    parent_diagram_id=part["parent_diagram_id"],
                    number=part["number"],
                    note=part["note"],
                    amount=part["amount"],
                    date_range=part["date_range"],
                )
            )

        diagrams.append(
            schemas.CreateDiagram(
                id=diagram_id,
                name=diagram_title,
                img_url=image_url,
                parent_group_id=souq_group.id,
            )
        )

    return [diagrams, parts]
