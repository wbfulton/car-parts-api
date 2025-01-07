from enum import Enum
from urllib.parse import urlencode, urlunsplit


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


def get_category_id(cat_name: SouqPartCategoryNames) -> SouqPartCategoryIds:
    category_map = {
        SouqPartCategoryNames.Body_Interior: SouqPartCategoryIds.Body_Interior,
        SouqPartCategoryNames.Engine: SouqPartCategoryIds.Engine,
        SouqPartCategoryNames.Power_Train_Chassis: SouqPartCategoryIds.Power_Train_Chassis,
        SouqPartCategoryNames.Electrical: SouqPartCategoryIds.Electrical,
    }
    return category_map[cat_name]


def get_category_ssd(cat_name: SouqPartCategoryNames) -> SouqPartCategorySsds:
    category_map = {
        SouqPartCategoryNames.Body_Interior: SouqPartCategorySsds.Body_Interior,
        SouqPartCategoryNames.Engine: SouqPartCategorySsds.Engine,
        SouqPartCategoryNames.Power_Train_Chassis: SouqPartCategorySsds.Power_Train_Chassis,
        SouqPartCategoryNames.Electrical: SouqPartCategorySsds.Electrical,
    }
    return category_map[cat_name]


def get_category_name(cat_id: SouqPartCategoryIds) -> SouqPartCategoryNames:
    category_map = {
        SouqPartCategoryIds.Body_Interior: SouqPartCategoryNames.Body_Interior,
        SouqPartCategoryIds.Engine: SouqPartCategoryNames.Engine,
        SouqPartCategoryIds.Power_Train_Chassis: SouqPartCategoryNames.Power_Train_Chassis,
        SouqPartCategoryIds.Electrical: SouqPartCategoryNames.Electrical,
    }
    return category_map[cat_id]


SCHEME = "https"
NETLOC = "partsouq.com"


def build_url(
    path: str,
    query: dict | str = "",
):
    encoded_query = urlencode(query)
    return urlunsplit((SCHEME, NETLOC, path, encoded_query, ""))
