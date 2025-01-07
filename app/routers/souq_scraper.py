from enum import Enum
from urllib.parse import parse_qs, urlencode, urlsplit, urlunsplit

from bs4 import BeautifulSoup
from fastapi import APIRouter
from seleniumbase import Driver

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


class SouqToolsUrlPath(str, Enum):
    categories = "/en/catalog/genuine/vehicle/"
    search = "/en/search/all/"
    groups = "/en/catalog/genuine/groups/"
    group_diagram = "/en/catalog/genuine/parts"
    diagram = "/en/catalog/genuine/unit/"


class SouqPartCategoryNames(str, Enum):
    Body_Interior = "Body/Interior"
    Engine = "Engine/Fuel/Tool"
    Power_Train_Chassis = "Power Train/Chassis"
    Electrical = "Electrical"


class SouqPartCategorySsds(str, Enum):
    Body_Interior = "$*KwGCtqev2eXR7dKE79ObiNrO7un3homEhZe4i8PF9uL--vj7vqmF78HFwfDm_-6otb-Ci_r2_vWW97uysuP05JeBgYbKh6eAksWUjZLrlJjLhNmKgsvJxtjS9JLFmNOTjJeSho-F3dLLkp2WldnFlI7Jxavx4_f6kp2WloSE2YqRlOLq-4eE2avW9__m8vvwlJjJxY3Tk4yX3sTa2MXH2dbY0pWKkYfJAAAAANxDhqI=$"
    Engine = "$*KwGlkYCI_sL2yvWjyPS8r_3pyc7Qoa6jorCfrOTi0cXZ3d_cmY6iyObi5tfB2MmPkpilrN3R2dKx0JyVlcTTw7CmpqHtoICnteKzqrXMs7_so_6tp-zu4f_107Xiv_S0q7C1oaii-vXstbqxsv7is6nu4ozWxNDdtbqxsaOj_q22s8XN3KCj_ozx0NjB1dzXs7_u4qr0tKuw-eP9_-Lg_vH_9bKttqDuAAAAAGoSyS8=$"
    Power_Train_Chassis = "$*KwE6Dh8XYV1pVWo8V2sjMGJ2VlFPPjE8PS8AM3t9TlpGQkBDBhE9V3l9eUheR1YQDQc6M0JORk0uTwMKCltMXC85OT5yPx84Kn0sNSpTLCBzPGEyO3NxfmBqTCp9IGsrNC8qPjc9ZWpzKiUuLWF9LDZxfRNJW09CKiUuLjw8YTIpLFpSQz88YRNuT0deSkNILCBxfTVrKzQvZnxiYH1_YW5gai0yKT9xAAAAADut90o=$"
    Electrical = "$*KwE4DB0VY19rV2g-VWkhMmB0VFNNPDM-Py0CMXl_TFhEQEJBBBM_VXt_e0pcRVQSDwU4MUBMRE8sTQEICFlOXi07OzxwPR06KH8uNyhRLiJxPmMwP3FzfGJoTih_ImkpNi0oPDU_Z2hxKCcsL2N_LjRzfxFLWU1AKCcsLD4-YzArLlhQQT0-YxFsTUVcSEFKLiJzfzdpKTYtZH5gYn99Y2xiaC8wKz1zAAAAAOeXifk=$"


class SouqPartCategoryIds(int, Enum):
    Body_Interior = 3
    Engine = 1
    Power_Train_Chassis = 2
    Electrical = 4


def get_category_id(cat_name: SouqPartCategoryNames):
    if cat_name == SouqPartCategoryNames.Body_Interior:
        return SouqPartCategoryIds.Engine
    if cat_name == SouqPartCategoryNames.Body_Interior:
        return SouqPartCategoryIds.Power_Train_Chassis
    if cat_name == SouqPartCategoryNames.Power_Train_Chassis:
        return SouqPartCategoryIds.Body_Interior
    if cat_name == SouqPartCategoryNames.Electrical:
        return SouqPartCategoryIds.Electrical


def get_category_ssd(cat_name: SouqPartCategoryNames):
    if cat_name == SouqPartCategoryNames.Body_Interior:
        return SouqPartCategorySsds.Engine
    if cat_name == SouqPartCategoryNames.Body_Interior:
        return SouqPartCategorySsds.Power_Train_Chassis
    if cat_name == SouqPartCategoryNames.Power_Train_Chassis:
        return SouqPartCategorySsds.Body_Interior
    if cat_name == SouqPartCategoryNames.Electrical:
        return SouqPartCategorySsds.Electrical


def get_category_name(cat_id: SouqPartCategoryIds):
    if cat_id == SouqPartCategoryIds.Body_Interior:
        return SouqPartCategoryNames.Engine
    if cat_id == SouqPartCategoryIds.Body_Interior:
        return SouqPartCategoryNames.Power_Train_Chassis
    if cat_id == SouqPartCategoryIds.Power_Train_Chassis:
        return SouqPartCategoryNames.Body_Interior
    if cat_id == SouqPartCategoryIds.Electrical:
        return SouqPartCategoryNames.Electrical


base_category_query: SouqQuery = {
    "c": "TOYOTA00",
    "ssd": "$*KwEcKDkxR3tPc0wacU0FFkRQcHdpGBcaGwkmFV1baHxgZGZlIDcbcV9bX254YXA2KyEcFWRoYGsIaSUsLH1qegkfHxhUGTkeDFsKEwx1CgZVGkcUHFVXWEZMagxbBk0NEgkMGBEbQ0xVDAMIC0dbChBXWzVvfWlkDAMICBoaRxQPCnx0ZRkaRzVIaWF4bGVuCgZXWxNNDRIJQFpERltZR0hGTAsUDxlXAAAAAA5ZBL4=$",
    "vid": "0",
    "cid": "",
    "cname": "",
    "q": "",
}

base_group_query: SouqQuery = {
    "c": "TOYOTA00",
    "ssd": "$*KwEpHQwEck56RnkvRHgwI3FlRUJcLSIvLjwTIGhuXUlVUVNQFQIuRGpualtNVEUDHhQpIFFdVV49XBAZGUhfTzwqKi1hLAwrOW4_JjlAPzNgL3IhK2BibnN5XzluM3J-PyYqNj95KyhyITgsLSsuPzNgJT45ID8tKikrLXUDcmZka3V_WmY9IS9yITo_KyIrKSpybnw7OHRoOSA9PRINAlpXPzA7OHB8YHZwOU9HVioqLVNvCx5LX1ZdOTY9PTQvciE6c2l3djE_YCo5fzgnPCpnAAAAALIWi4w=$",
    "vid": "0",
    "cid": "2",
    "q": "",
}

electical_cat_query: SouqQuery = {
    "c": "TOYOTA00",
    "ssd": "$*KwEpHQwEck56RnkvRHgwI3FlRUJcLSIvLjwTIGhuXUlVUVNQFQIuRGpualtNVEUDHhQpIFFdVV49XBAZGUhfTzwqKi1hLAwrOW4_JjlAPzNgL3IhK2BibnN5XzluM3J-PyYqNj95KyhyITgsLSsuPzNgJT45ID8tKikrLXUDcmZka3V_WmY9IS9yITo_KyIrKSpybnw7OHRoOSA9PRINAlpXPzA7OHB8YHZwOU9HVioqLVNvCx5LX1ZdOTY9PTQvciE6c2l3djE_YCo5fzgnPCpnAAAAALIWi4w=$",
    "vid": "0",
    "cid": "2",
    "q": "",
}


SCHEME = "https"
NETLOC = "partsouq.com"

souq_base_url = f"{SCHEME}://{NETLOC}"


def build_souq_url(
    path: SouqToolsUrlPath,
    query: SouqQuery | None = None,
):
    encoded_query = urlencode(query)
    return urlunsplit((SCHEME, NETLOC, path, encoded_query, ""))


@router.get("/")
async def get_everything_by_category(
    part_category: SouqPartCategoryNames,
) -> Everything:
    # get categories
    # get diagrams in each category
    # get parts in each diagram
    diagrams: list[SouqDiagram] = []
    parts: list[SouqPart] = []
    cat_diagrams = await get_category_diagrams(part_category=part_category)
    for diagram in cat_diagrams:
        diagrams.append(diagram)
        diagram_parts = await get_diagram_parts(souq_diagram=diagram)
        for part in diagram_parts:
            parts.append(part)
    # get parts in each diagram
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
async def get_part_groups() -> dict[str, list[SouqPartGroup]]:
    # initialize the driver in GUI mode with UC enabled
    driver = Driver(uc=True, headless=False)
    url = build_souq_url(SouqToolsUrlPath.groups, base_group_query)
    # open URL with a 6-second reconnect time to bypass the initial JS challenge
    driver.uc_open_with_reconnect(url, reconnect_time=6)

    soup = BeautifulSoup(driver.page_source, "html5lib")
    diagrams_data: list[SouqPartGroup] = []

    tbody = soup.find(
        "table", class_="table-mage table table-bordered- table-stripped tree"
    ).contents[0]  # go through recursively
    for row in tbody.contents[1:]:
        name = row.get_text().strip()
        classes: list[str] = row.attrs["class"]
        group_number = list(
            filter(
                lambda class_string: "treegrid-" in class_string
                and "treegrid-parent-" not in class_string,
                classes,
            )
        )
        group_number = group_number[0].split("-")[-1].strip()

        parent_arr = list(
            filter(
                lambda class_string: "treegrid-" in class_string
                and "treegrid-parent-" in class_string,
                classes,
            )
        )
        parent_group_number = (
            None
            if parent_arr is None or len(parent_arr) == 0
            else parent_arr[0].split("-")[-1].strip()
        )

        a_tag = row.find("a")

        car = None
        souq_gid = None
        ssd = None

        if a_tag is not None:
            diagram_url = souq_base_url + row.find("a").get_attribute_list("href")[0]

            souq_deets = parse_qs(urlsplit(diagram_url)[3])

            # query
            car = souq_deets["c"][0]
            souq_gid = souq_deets["gid"][0]
            ssd = souq_deets["ssd"][0]

        diagrams_data.append(
            {
                "name": name,
                "group_number": group_number,
                "parent_group_number": parent_group_number,
                "souq_gid": souq_gid,
                "car": car,
                "ssd": ssd,
            }
        )

    # close the browser
    driver.quit()

    # create map
    parent_map: dict[str, list[SouqPartGroup]] = dict({})
    for diagram in diagrams_data:
        parent = diagram["parent_group_number"]
        if parent is None:
            parent = "0"

        if parent not in parent_map:
            parent_map[parent] = [diagram]
        else:
            parent_map[parent].append(diagram)

    return parent_map


@router.post("/group-diagram-parts")
async def get_group_diagram_parts(
    souq_diagram: SouqPartGroup,
) -> list[SouqGroupDiagram]:
    # initialize the driver in GUI mode with UC enabled
    driver = Driver(uc=True, headless=False)

    query: SouqQuery = {
        "c": souq_diagram["car"],
        "ssd": souq_diagram["ssd"],
        "gid": souq_diagram["souq_gid"],
        "vid": 0,
        "q": "",
    }

    url = build_souq_url(SouqToolsUrlPath.group_diagram, query=query)
    # open URL with a 6-second reconnect time to bypass the initial JS challenge
    driver.uc_open_with_reconnect(url, reconnect_time=6)

    soup = BeautifulSoup(driver.page_source, "html5lib")
    diagrams: list[SouqGroupDiagram] = []

    # part_rows = soup.find_all("tr", class_="part-search-tr")
    panels = soup.find_all("div", class_="panel panel-default")

    for panel in panels:
        [heading, body] = panel.contents
        title = heading.find("h2").text.strip()
        [table, img] = body.contents[0].contents
        # img url
        img_url = souq_base_url + img.find("img").get_attribute_list("src")[0]
        # parts
        part_rows = table.find("tbody").contents

        parts: list[SouqPart] = []
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
                    "ssd": souq_diagram["ssd"],
                    "souq_gid": souq_diagram["souq_gid"],
                }
            )

        diagrams.append(
            {
                "title": title,
                "img_url": img_url,
                "parts": parts,
                "gid": souq_diagram["souq_gid"],
            }
        )

    # close the browser
    driver.quit()

    return diagrams


@router.get("/category-diagrams")
async def get_category_diagrams(
    part_category: SouqPartCategoryNames,
) -> list[SouqDiagram]:
    # initialize the driver in GUI mode with UC enabled
    driver = Driver(uc=True, headless=False)

    query = dict(base_category_query)
    query["ssd"] = get_category_ssd(part_category.value).value
    query["cname"] = part_category.value
    query["cid"] = get_category_id(part_category).value

    url = build_souq_url(SouqToolsUrlPath.categories, query)
    # open URL with a 6-second reconnect time to bypass the initial JS challenge
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
        img_urls = list(map(lambda url: souq_base_url + url, img_urls))

        caption = diagram.find("h5").find("a")
        [number, title] = caption.text.split(":")

        diagram_url = souq_base_url + caption.get_attribute_list("href")[0]

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

    # close the browser
    driver.quit()

    return diagrams_data


@router.post("/diagram-parts")
async def get_diagram_parts(
    souq_diagram: SouqDiagram,
) -> list[SouqPart]:
    # initialize the driver in GUI mode with UC enabled
    driver = Driver(uc=True, headless=False)

    query: SouqQuery = {
        "c": souq_diagram["car"],
        "ssd": souq_diagram["ssd"],
        "uid": souq_diagram["souq_uid"],
        "cid": souq_diagram["cid"],
    }
    url = build_souq_url(SouqToolsUrlPath.diagram, query=query)
    # open URL with a 6-second reconnect time to bypass the initial JS challenge
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

    # close the browser
    driver.quit()

    return parts


@router.post("/parts/{part_number}")
async def get_part_search_list(part_number: str) -> list[SouqSearchPart]:
    # initialize the driver in GUI mode with UC enabled
    driver = Driver(uc=True, headless=False)

    query: SouqQuery = {
        "q": part_number,
    }
    url = build_souq_url(SouqToolsUrlPath.search, query=query)
    # open URL with a 6-second reconnect time to bypass the initial JS challenge
    driver.uc_open_with_reconnect(url, reconnect_time=6)

    soup = BeautifulSoup(driver.page_source, "html5lib")
    parts: list[SouqSearchPart] = []

    search_rows = soup.find_all("div", class_="product-col list clearfix")
    # search_rows = soup.find_all("div", class_="search-result-container")

    for search_row in search_rows:
        [diagram, details, price_section] = search_row.contents[0].contents

        img_url = souq_base_url + diagram.find("img").get_attribute_list("src")[0]
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

    # close the browser
    driver.quit()

    return parts
