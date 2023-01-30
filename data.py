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
    with open(get_file(day, meal), "w") as file:
        json.dump(menu_data, file)
    return menu_data


CACHE = xdg.xdg_cache_home() / "rofi-cafmenu"
"""The directory in which we cache the json menus."""
CACHE.mkdir(parents=True, exist_ok=True)


def get_file(day: datetime.datetime, meal: Meal) -> pathlib.Path:
    """Returns the filename for the json file representing the `meal` on the specific `day`."""
    return CACHE / f"{day.date().isoformat()}-{meal.name}.json"


def get_cached_menu(day: datetime.datetime, meal: Meal) -> typing.Any | None:
    """Returns the cached json menu for this meal if it exists."""
    try:
        with open(get_file(day, meal), "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return None
