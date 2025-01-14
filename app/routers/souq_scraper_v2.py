import asyncio
from typing import Tuple
from urllib.parse import parse_qs, urlsplit

from bs4 import BeautifulSoup
from fastapi import APIRouter
from seleniumbase import Driver

from app.routers.utils import (
    SouqToolsUrlPath,
    build_url,
)
from app.schemas import (
    CreateDiagram,
    CreateGroup,
    CreatePart,
    Group,
    Part,
    PartDetailed,
    SouqQuery,
)

path_tag = "/souq/v2"


router = APIRouter(
    prefix=path_tag,
    tags=[path_tag],
)


@router.get("/group")
async def scrape_groups() -> list[CreateGroup]:
    group_query: SouqQuery = {
        "c": "TOYOTA00",
        "ssd": "$*KwEpHQwEck56RnkvRHgwI3FlRUJcLSIvLjwTIGhuXUlVUVNQFQIuRGpualtNVEUDHhQpIFFdVV49XBAZGUhfTzwqKi1hLAwrOW4_JjlAPzNgL3IhK2BibnN5XzluM3J-PyYqNj95KyhyITgsLSsuPzNgJT45ID8tKikrLXUDcmZka3V_WmY9IS9yITo_KyIrKSpybnw7OHRoOSA9PRINAlpXPzA7OHB8YHZwOU9HVioqLVNvCx5LX1ZdOTY9PTQvciE6c2l3djE_YCo5fzgnPCpnAAAAALIWi4w=$",
        "vid": "0",
        "cid": "0",
        "q": "",
    }

    url = build_url(SouqToolsUrlPath.groups, group_query)
    driver = Driver(uc=True, headless=True)
    driver.uc_open_with_reconnect(url, reconnect_time=4)

    soup = BeautifulSoup(driver.page_source, "html5lib")
    groups_table = soup.find(
        "table", class_="table-mage table table-bordered- table-stripped tree"
    )
    groups: list[CreateGroup] = []

    rows = groups_table.contents[0].contents[1:]

    for row in rows:
        group_name = row.get_text().strip()
        css_classes: list[str] = row.attrs["class"]

        # Extract group number
        id = next(
            (
                cls.split("-")[-1].strip()
                for cls in css_classes
                if "treegrid-" in cls and "treegrid-parent-" not in cls
            ),
            None,
        )

        # Determine if this is a root group
        parent_id = next(
            (
                cls.split("-")[-1].strip()
                for cls in css_classes
                if "treegrid-parent-" in cls
            ),
            None,
        )

        # Extract link data if exists
        link = row.find("a")
        if link:
            link = build_url(link["href"])

        group = CreateGroup(
            id=int(id),
            name=group_name,
            diagrams_url=link,
            parent_group_id=parent_id,
        )

        groups.append(group)

    driver.quit()
    return groups


# pagination is for the valid groups, not diagrams
@router.post("/diagrams")
async def get_diagrams(page_length: int = 435, token: int = 0) -> list[CreateDiagram]:
    # # Get groups first
    groups = await scrape_groups()
    diagrams: list[CreateDiagram] = []

    valid_groups: list[Group] = []
    for group in groups:
        group = Group(**group)
        if len(group.groups) == 0:
            valid_groups.append(group)

    # 435 total
    valid_groups: list[Group] = groups[token : token + page_length]

    for i, group in enumerate(valid_groups):
        try:
            [
                new_diagrams,
            ] = await scrape_group_diagrams(souq_group=group)
            diagrams = diagrams + new_diagrams
            # Add small delay between requests
            await asyncio.sleep(1)
        except Exception as e:
            print(f"Error processing group {str(group)}: {str(e)}")
            continue

    return diagrams


@router.post("/group/save")
async def scrape_save_group_diagrams(
    souq_group: Group,
) -> Tuple[str, str]:
    if isinstance(souq_group, dict):
        souq_group = Group(**souq_group)

    url_params = parse_qs(urlsplit(souq_group.diagrams_url)[3])
    query: SouqQuery = {
        "c": url_params["c"][0],
        "ssd": url_params["ssd"][0],
        "gid": url_params["gid"][0],
        "vid": 0,
        "q": "",
    }
    url = build_url(SouqToolsUrlPath.group_diagram, query=query)
    driver = Driver(uc=True, headless=True)
    driver.uc_open_with_reconnect(url, reconnect_time=4)

    soup = BeautifulSoup(driver.page_source, "html5lib")

    driver.quit()
    return [url, str(soup)]


@router.post("/group/diagrams")
async def scrape_group_diagrams(
    souq_group: Group,
) -> Tuple[list[CreateDiagram], list[Part]]:
    if isinstance(souq_group, dict):
        souq_group = Group(**souq_group)

    url_params = parse_qs(urlsplit(souq_group.diagrams_url)[3])
    query: SouqQuery = {
        "c": url_params["c"][0],
        "ssd": url_params["ssd"][0],
        "gid": url_params["gid"][0],
        "vid": 0,
        "q": "",
    }
    url = build_url(SouqToolsUrlPath.group_diagram, query=query)
    driver = Driver(uc=True, headless=True)
    driver.uc_open_with_reconnect(url, reconnect_time=4)

    soup = BeautifulSoup(driver.page_source, "html5lib")

    diagram_panels = soup.find_all("div", class_="panel panel-default")
    diagrams: list[CreateDiagram] = []
    parts: list[CreatePart] = []

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
            part = {
                "name": str(name.text.strip()),
                "parent_diagram_id": diagram_id,
                "number": str(number.text.strip()),
                "note": note.text.strip(),
                "amount": amount,
                "date_range": date_range.text.strip(),
            }

            parts.append(
                CreatePart(
                    name=part["name"],
                    parent_diagram_id=part["parent_diagram_id"],
                    number=part["number"],
                    note=part["note"],
                    amount=part["amount"],
                    date_range=part["date_range"],
                )
            )

        diagrams.append(
            CreateDiagram(
                id=diagram_id,
                name=diagram_title,
                img_url=image_url,
                parent_group_id=souq_group.id,
            )
        )

    driver.quit()
    return [diagrams, parts]


@router.post("/parts/{part_number}")
async def get_part_search_list(
    part_number: str,
) -> list[PartDetailed]:
    query: SouqQuery = {
        "q": part_number,
    }
    url = build_url(SouqToolsUrlPath.search, query=query)
    driver = Driver(uc=True, headless=True)
    driver.uc_open_with_reconnect(url, reconnect_time=4)

    soup = BeautifulSoup(driver.page_source, "html5lib")
    parts: list[PartDetailed] = []

    search_rows = soup.find_all("div", class_="product-col list clearfix")

    for search_row in search_rows:
        [diagram, details, price_section] = search_row.contents[0].contents

        img_url = build_url(diagram.find("img").get_attribute_list("src")[0])
        name = details.find("h1").text.strip()
        part_number = details.find("h2").text.split(":")[1].strip()
        parts_avaliable = details.find("p", class_="mb-10px").text[-1].strip()
        weight_kg = (
            details.find("p", class_="hidden-xs mb-10px").text.split(":")[1].strip()
        )

        price = price_section.find("span", "price-new").text[:-1].strip()

        parts.append(
            {
                "name": name,
                "part_number": part_number,
                "parts_avaliable": parts_avaliable,
                "weight_kg": weight_kg,
                "price_usd": price,
                "img_url": img_url,
            }
        )

    driver.quit()
    return parts


def parse_table_row(row: BeautifulSoup) -> dict:
    """Helper to parse table rows consistently"""
    columns = row.find_all("td")
    return {
        "name": columns[1].text.strip() if len(columns) > 1 else "",
        "number": columns[0].text.strip() if columns else "",
        "part_code": columns[2].text.strip() if len(columns) > 2 else "",
        "note": columns[3].text.strip() if len(columns) > 3 else "",
        "amount": columns[4].text.strip() if len(columns) > 4 else "",
        "date_range": columns[5].text.strip() if len(columns) > 5 else "",
    }
