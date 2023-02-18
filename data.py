import datetime
import enum
import json
import pathlib
import typing

import requests
import xdg


class Meal(enum.Enum):
    """The numbers associated with each meal are the numbers CampusDish uses for Carleton's meals as of Winter 2023."""
    BREAKFAST = 2082
    LUNCH = 2084
    DINNER = 2085


API_URL = "https://carleton.campusdish.com/api/menu/GetMenus"
"""The URL for Carleton's CampusDish API."""
PARAMS = "?locationId=5087&storeIds=&mode=Daily&date={}/{}/{}&time=&periodId={}&fulfillmentMethod="
"""A format string for the parameters used to retrieve menu data.

>>> PARAMS.format(month, day, year, meal)

The meal value is the appropriate integer from the Meal enum."""


def cache_menu(day: datetime.datetime, meal: Meal) -> typing.Any | None:
    """Caches the json menu locally and returns it, if it exists."""
    menu = requests.get(API_URL + PARAMS.format(day.month, day.day, day.year, meal.value))
    if not menu.ok:
        return
    menu_data = menu.json()
    with open(get_meal_file(day, meal), "w") as file:
        json.dump(menu_data, file)
    return menu_data


APP_NAME = "rofi-cafmenu"
"""The directory that config and cache information is stored in"""

CACHE = xdg.xdg_cache_home() / APP_NAME
"""The directory in which we cache the json menus."""
CACHE.mkdir(parents=True, exist_ok=True)


def get_meal_file(day: datetime.datetime, meal: Meal) -> pathlib.Path:
    """Returns the filename for the json file representing the `meal` on the specific `day`."""
    return CACHE / f"{day.date().isoformat()}-{meal.name}.json"


def get_cached_menu(day: datetime.datetime, meal: Meal) -> typing.Any | None:
    """Returns the cached json menu for this meal if it exists."""
    try:
        with open(get_meal_file(day, meal), "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return None


CONFIG = xdg.xdg_config_home() / APP_NAME
"""The directory in which we store the configuration for the menus."""
CONFIG.mkdir(parents=True, exist_ok=True)


def get_configuration() -> dict[str: typing.Any]:
    """Returns the JSON data from the config file."""
    config_path = CONFIG / "config.json"
    if config_path.exists() and config_path.is_file():
        return json.loads(config_path.read_text())
    return {}


configuration = get_configuration()


def get_config_item(item: str) -> typing.Any | None:
    """Retrieve a field from the configuration, if it exists."""
    if item in configuration:
        return configuration[item]


def ignored_dishes() -> list[str]:
    """Retrieve a list of dishes to not display."""
    return get_config_item("ignored-items") or []


def ignored_meals() -> list[str]:
    """Retrieve a list of mealtimes to not display."""
    return get_config_item("ignored-meals") or []


def ignored_stations() -> list[str]:
    """Retrieve a list of stations to not display."""
    return get_config_item("ignored-stations") or []
