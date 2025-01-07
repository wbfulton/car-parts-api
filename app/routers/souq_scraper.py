from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
from urllib.parse import parse_qs, urlsplit

from bs4 import BeautifulSoup
from fastapi import APIRouter, Depends
from seleniumbase import Driver

from app.routers.utils import (
    SouqPartCategoryNames,
    SouqToolsUrlPath,
    build_url,
    get_category_id,
    get_category_ssd,
)
from app.schemas.souq import (
    Everything,
    SouqDiagram,
    SouqGroupDiagram,
    SouqPart,
    SouqPartGroup,
    SouqQuery,
    SouqSearchPart,
)

path_tag = "/souq"


router = APIRouter(
    prefix=path_tag,
    tags=[path_tag],
)


class DriverManager:
    _instance: Optional[Driver] = None

    @classmethod
    def get_driver(cls) -> Driver:
        if cls._instance is None:
            if cls._instance is not None:
                cls._instance.quit()
            cls._instance = Driver(uc=True, headless=False)
        return cls._instance

    @classmethod
    def quit(cls):
        if cls._instance is not None:
            cls._instance.quit()
            cls._instance = None


@router.on_event("startup")
async def startup_event():
    DriverManager.get_driver()


@router.on_event("shutdown")
def shutdown_event():
    DriverManager.quit()


@asynccontextmanager
async def get_selenium_driver() -> AsyncGenerator[Driver, None]:
    try:
        driver = DriverManager.get_driver()
        yield driver
    except Exception as e:
        DriverManager.quit()
        raise e


@router.get("/")
async def get_everything_by_category(
    part_category: SouqPartCategoryNames, driver: Driver = Depends(get_selenium_driver)
) -> Everything:
    diagrams: list[SouqDiagram] = []
    parts: list[SouqPart] = []

    # Pass the driver to the helper functions
    cat_diagrams = await get_category_diagrams(
        part_category=part_category, driver=driver
    )

    for diagram in cat_diagrams:
        diagrams.append(diagram)
        diagram_parts = await get_diagram_parts(souq_diagram=diagram, driver=driver)
        parts.extend(diagram_parts)

    return {"part_category": part_category, "diagrams": diagrams, "parts": parts}


@router.get("/all-group-diagram-parts")
async def get_all_group_diagram_parts(
    page_length: int = 20, token: int = 0
) -> list[SouqGroupDiagram]:
    # get categories
    groups = await get_part_groups()

    diagrams: list[SouqGroupDiagram] = []
    count = 0
    for key in groups.keys():
        for group in groups[key]:
            if (
                group["souq_gid"] is not None
                and group["car"] is not None
                and group["ssd"] is not None
            ):
                count += 1
                if count < token + page_length:
                    diagrams_parts = await get_group_diagram_parts(souq_diagram=group)
                    for diagram in diagrams_parts:
                        diagrams.append(diagram)

    # get parts in each diagram
    return diagrams


@router.get("/part-groups")
async def get_part_groups(
    driver: Driver = Depends(get_selenium_driver),
) -> dict[str, list[SouqPartGroup]]:
    group_query: SouqQuery = {
        "c": "TOYOTA00",
        "ssd": "$*KwEpHQwEck56RnkvRHgwI3FlRUJcLSIvLjwTIGhuXUlVUVNQFQIuRGpualtNVEUDHhQpIFFdVV49XBAZGUhfTzwqKi1hLAwrOW4_JjlAPzNgL3IhK2BibnN5XzluM3J-PyYqNj95KyhyITgsLSsuPzNgJT45ID8tKikrLXUDcmZka3V_WmY9IS9yITo_KyIrKSpybnw7OHRoOSA9PRINAlpXPzA7OHB8YHZwOU9HVioqLVNvCx5LX1ZdOTY9PTQvciE6c2l3djE_YCo5fzgnPCpnAAAAALIWi4w=$",
        "vid": "0",
        "cid": "2",  # fix this
        "q": "",
    }

    url = build_url(SouqToolsUrlPath.groups, group_query)
    driver.uc_open_with_reconnect(url, reconnect_time=6)

    soup = BeautifulSoup(driver.page_source, "html5lib")
    groups_table = soup.find(
        "table", class_="table-mage table table-bordered- table-stripped tree"
    )
    groups_data: list[SouqPartGroup] = []

    for row in groups_table.contents[0].contents[1:]:
        group_name = row.get_text().strip()
        css_classes: list[str] = row.attrs["class"]

        # Extract group number
        group_number = next(
            (
                cls.split("-")[-1].strip()
                for cls in css_classes
                if "treegrid-" in cls and "treegrid-parent-" not in cls
            ),
            None,
        )

        # Extract parent group number
        parent_number = next(
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
            diagram_url = build_url(link["href"])
            url_params = parse_qs(urlsplit(diagram_url)[3])
            car = url_params["c"][0]
            group_id = url_params["gid"][0]
            ssd = url_params["ssd"][0]
        else:
            car = group_id = ssd = None

        groups_data.append(
            {
                "name": group_name,
                "group_number": group_number,
                "parent_group_number": parent_number,
                "souq_gid": group_id,
                "car": car,
                "ssd": ssd,
            }
        )

    # Group by parent
    grouped_data: dict[str, list[SouqPartGroup]] = {}
    for group in groups_data:
        parent = group["parent_group_number"] or "0"
        if parent not in grouped_data:
            grouped_data[parent] = []
        grouped_data[parent].append(group)

    return grouped_data


@router.post("/group-diagram-parts")
async def get_group_diagram_parts(
    souq_diagram: SouqPartGroup, _driver: Driver = Depends(get_selenium_driver)
) -> list[SouqGroupDiagram]:
    async with _driver as driver:
        query: SouqQuery = {
            "c": souq_diagram.car,
            "ssd": souq_diagram.ssd,
            "gid": souq_diagram.souq_gid,
            "vid": 0,
            "q": "",
        }

        url = build_url(SouqToolsUrlPath.group_diagram, query=query)
        driver.uc_open_with_reconnect(url, reconnect_time=6)

        soup = BeautifulSoup(driver.page_source, "html5lib")
        diagram_panels = soup.find_all("div", class_="panel panel-default")
        diagrams: list[SouqGroupDiagram] = []

        for panel in diagram_panels:
            header, body = panel.contents
            diagram_title = header.find("h2").text.strip()

            content_section = body.contents[0]
            parts_table, diagram_image = content_section.contents

            image_url = build_url(diagram_image.find("img")["src"])

            # Parse parts
            parts_rows = parts_table.find("tbody").contents
            diagram_parts: list[SouqPart] = []

            for row in parts_rows:
                number, name, part_code, note, amount, date_range = row.contents

                diagram_parts.append(
                    {
                        "name": name.text.strip(),
                        "number": number.text.strip(),
                        "part_code": part_code.text.strip(),
                        "note": note.text.strip(),
                        "amount": amount.text.strip(),
                        "date_range": date_range.text.strip(),
                        "car": souq_diagram.car,
                        "ssd": souq_diagram.ssd,
                        "souq_gid": souq_diagram.souq_gid,
                    }
                )

            diagrams.append(
                {
                    "title": diagram_title,
                    "img_url": image_url,
                    "parts": diagram_parts,
                    "gid": souq_diagram.souq_gid,
                }
            )

        return diagrams


@router.get("/category-diagrams")
async def get_category_diagrams(
    part_category: SouqPartCategoryNames, driver: Driver = Depends(get_selenium_driver)
) -> list[SouqDiagram]:
    query: SouqQuery = {
        "ssd": get_category_ssd(part_category.value).value,
        "cname": part_category.value,
        "cid": get_category_id(part_category).value,
        "c": "TOYOTA00",
        "vid": "0",
        "q": "",
    }

    url = build_url(SouqToolsUrlPath.categories, query)
    driver.uc_open_with_reconnect(url, reconnect_time=6)

    soup = BeautifulSoup(driver.page_source, "html5lib")
    diagrams_data: list[SouqDiagram] = []

    diagrams = soup.find_all("div", "thumbnail thumb-boss")
    for diagram in diagrams:
        img = diagram.find(
            "img", class_="ezoom-vehicle-ondemand vehicle-category-image"
        )

        img_urls = img.get_attribute_list("data-zoom-image") + img.get_attribute_list(
            "src"
        )
        img_urls = list(map(lambda url: build_url(url), img_urls))

        caption = diagram.find("h5").find("a")
        [number, title] = caption.text.split(":")

        diagram_url = build_url(caption.get_attribute_list("href")[0])

        souq_deets = parse_qs(urlsplit(diagram_url)[3])

        diagrams_data.append(
            {
                "title": title.strip(),
                "number": number.strip(),
                "car": souq_deets["c"][0],
                "souq_uid": souq_deets["uid"][0],
                "ssd": souq_deets["ssd"][0],
                "cid": souq_deets["cid"][0],
                "image_urls": img_urls,
            }
        )

    return diagrams_data


@router.post("/diagram-parts")
async def get_diagram_parts(
    souq_diagram: SouqDiagram, driver: Driver = Depends(get_selenium_driver)
) -> list[SouqPart]:
    query: SouqQuery = {
        "c": souq_diagram["car"],
        "ssd": souq_diagram["ssd"],
        "uid": souq_diagram["souq_uid"],
        "cid": souq_diagram["cid"],
    }
    url = build_url(SouqToolsUrlPath.diagram, query=query)
    driver.uc_open_with_reconnect(url, reconnect_time=6)

    soup = BeautifulSoup(driver.page_source, "html5lib")
    parts: list[SouqPart] = []

    part_rows = soup.find_all("tr", class_="part-search-tr")
    for part_row in part_rows:
        [number, name, part_code, note, amount, range] = part_row.contents

        parts.append(
            {
                "name": name.text.strip(),
                "number": number.text.strip(),
                "part_code": part_code.text.strip(),
                "note": note.text.strip(),
                "amount": amount.text.strip(),
                "date_range": range.text.strip(),
                "car": souq_diagram["car"],
                "diagram_uid": souq_diagram["souq_uid"],
                "cid": souq_diagram["cid"],
            }
        )

    return parts


@router.post("/parts/{part_number}")
async def get_part_search_list(
    part_number: str, driver: Driver = Depends(get_selenium_driver)
) -> list[SouqSearchPart]:
    query: SouqQuery = {
        "q": part_number,
    }
    url = build_url(SouqToolsUrlPath.search, query=query)
    driver.uc_open_with_reconnect(url, reconnect_time=6)

    soup = BeautifulSoup(driver.page_source, "html5lib")
    parts: list[SouqSearchPart] = []

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

    return parts
