import asyncio
from urllib.parse import parse_qs, urlsplit

from bs4 import BeautifulSoup
from fastapi import APIRouter
from seleniumbase import Driver

from app.routers.utils import (
    SouqPartCategoryNames,
    SouqToolsUrlPath,
    build_url,
    get_category_id,
    get_category_ssd,
)
from app.schemas_old.souq import (
    Everything,
    SouqCategoryDiagram,
    SouqCategoryPart,
    SouqGroup,
    SouqGroupDiagram,
    SouqQuery,
    SouqSearchPart,
)

path_tag = "/souq"


router = APIRouter(
    prefix=path_tag,
    tags=[path_tag],
)


@router.get("/")
async def get_everything_by_category(
    part_category: SouqPartCategoryNames,
) -> Everything:
    diagrams: list[SouqCategoryDiagram] = []
    parts: list[SouqCategoryPart] = []

    cat_diagrams = await get_category_diagrams(part_category=part_category)

    for diagram in cat_diagrams:
        diagrams.append(diagram)
        diagram_parts = await get_catalog_diagram_parts(souq_diagram=diagram)
        parts.extend(diagram_parts)

    return {"part_category": part_category, "diagrams": diagrams, "parts": parts}


# Map of group id to diagrams
# TEMPORARY
@router.get("/group/diagrams/map")
async def get_all_group_diagrams(
    page_length: int = 20, token: int = 0
) -> dict[str, list[SouqGroupDiagram]]:
    # Get groups first
    groups = await get_groups()
    groups_diagrams: dict[str, list[SouqGroupDiagram]] = {}

    valid_groups: list[SouqGroup] = [
        group
        for key in groups.keys()
        for group in groups[key]
        if all(group.get(field) for field in ["souq_gid", "car", "ssd"])
    ]

    # Paginate results
    paginated_groups: list[SouqGroup] = valid_groups[token : token + page_length]

    for group in paginated_groups:
        try:
            diagrams = await get_group_diagrams(souq_group=group)
            groups_diagrams[group["souq_gid"]] = diagrams
            # Add small delay between requests
            await asyncio.sleep(1)
        except Exception as e:
            print(f"Error processing group {group['souq_gid']}: {str(e)}")
            continue

    return groups_diagrams


@router.get("/group")
async def get_groups() -> dict[str, list[SouqGroup]]:
    group_query: SouqQuery = {
        "c": "TOYOTA00",
        "ssd": "$*KwEpHQwEck56RnkvRHgwI3FlRUJcLSIvLjwTIGhuXUlVUVNQFQIuRGpualtNVEUDHhQpIFFdVV49XBAZGUhfTzwqKi1hLAwrOW4_JjlAPzNgL3IhK2BibnN5XzluM3J-PyYqNj95KyhyITgsLSsuPzNgJT45ID8tKikrLXUDcmZka3V_WmY9IS9yITo_KyIrKSpybnw7OHRoOSA9PRINAlpXPzA7OHB8YHZwOU9HVioqLVNvCx5LX1ZdOTY9PTQvciE6c2l3djE_YCo5fzgnPCpnAAAAALIWi4w=$",
        "vid": "0",
        "cid": "2",
        "q": "",
    }

    url = build_url(SouqToolsUrlPath.groups, group_query)
    driver = Driver(uc=True, headless=False)
    driver.uc_open_with_reconnect(url, reconnect_time=4)

    soup = BeautifulSoup(driver.page_source, "html5lib")
    groups_table = soup.find(
        "table", class_="table-mage table table-bordered- table-stripped tree"
    )
    groups_data: list[SouqGroup] = []

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
    grouped_data: dict[str, list[SouqGroup]] = {}
    for group in groups_data:
        parent = group["parent_group_number"] or "0"
        if parent not in grouped_data:
            grouped_data[parent] = []
        grouped_data[parent].append(group)

    driver.quit()
    return grouped_data


@router.post("/group/diagrams")
async def get_group_diagrams(souq_group: SouqGroup) -> list[SouqGroupDiagram]:
    souq_group = SouqGroup(**souq_group)

    query: SouqQuery = {
        "c": souq_group.car,
        "ssd": souq_group.ssd,
        "gid": souq_group.souq_gid,
        "vid": 0,
        "q": "",
    }
    url = build_url(SouqToolsUrlPath.group_diagram, query=query)
    driver = Driver(uc=True, headless=False)
    driver.uc_open_with_reconnect(url, reconnect_time=4)

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
        diagram_parts: list[SouqCategoryPart] = []

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
                    "car": souq_group.car,
                    "ssd": souq_group.ssd,
                    "souq_gid": souq_group.souq_gid,
                }
            )

        diagrams.append(
            {
                "title": diagram_title,
                "img_url": image_url,
                "parts": diagram_parts,
                "gid": souq_group.souq_gid,
            }
        )

    driver.quit()
    return diagrams


@router.get("/category-diagram")
async def get_category_diagrams(
    part_category: SouqPartCategoryNames,
) -> list[SouqCategoryDiagram]:
    query: SouqQuery = {
        "ssd": get_category_ssd(part_category.value).value,
        "cname": part_category.value,
        "cid": get_category_id(part_category).value,
        "c": "TOYOTA00",
        "vid": "0",
        "q": "",
    }

    url = build_url(SouqToolsUrlPath.categories, query)
    driver = Driver(uc=True, headless=False)
    driver.uc_open_with_reconnect(url, reconnect_time=4)

    soup = BeautifulSoup(driver.page_source, "html5lib")
    diagrams_data: list[SouqCategoryDiagram] = []

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

    driver.quit()
    return diagrams_data


# Returns parts for a standard diagram
@router.post("/catalog-diagram/parts")
async def get_catalog_diagram_parts(
    souq_diagram: SouqCategoryDiagram,
) -> list[SouqCategoryPart]:
    query: SouqQuery = {
        "c": souq_diagram.car,
        "ssd": souq_diagram.ssd,
        "uid": souq_diagram.souq_uid,
        "cid": souq_diagram.cid,
    }
    url = build_url(SouqToolsUrlPath.diagram, query=query)
    driver = Driver(uc=True, headless=False)
    driver.uc_open_with_reconnect(url, reconnect_time=4)

    soup = BeautifulSoup(driver.page_source, "html5lib")
    parts: list[SouqCategoryPart] = []

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
                "car": souq_diagram.car,
                "diagram_uid": souq_diagram.souq_uid,
                "cid": souq_diagram.cid,
            }
        )

    driver.quit()
    return parts


@router.post("/parts/{part_number}")
async def get_part_search_list(
    part_number: str,
) -> list[SouqSearchPart]:
    query: SouqQuery = {
        "q": part_number,
    }
    url = build_url(SouqToolsUrlPath.search, query=query)
    driver = Driver(uc=True, headless=False)
    driver.uc_open_with_reconnect(url, reconnect_time=4)

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
