import enum
import re

SERVER_URL = "https://lordsandknights.com"

LEVEL_COMPILED = re.compile(r"level (\d+)", re.IGNORECASE)


class HabitatType(enum.StrEnum):
    CASTLE = "castle"
    FORTRESS = "fortress"
    CITY = "city"


class ResearchBuilding(enum.StrEnum):
    UNIVERSITY = "University"
    LIBRARY = "Library"


HABITAT_TYPE_MAP = {
    "Ore store": HabitatType.CASTLE,
    "Ore Storage": HabitatType.FORTRESS,
    "Ore Depot": HabitatType.CITY,
}

# to be used only with playwright
SECOND = 1000.0
MINUTE = 60 * SECOND
