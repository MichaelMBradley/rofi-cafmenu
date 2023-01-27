#!./venv/bin/python
import enum
import json
import datetime

import requests
import rofi_menu
import xdg


class Meal(enum.Enum):
    BREAKFAST = 2082
    LUNCH = 2084
    DINNER = 2085


def get_meals(start_day: datetime.date, num_days: int):
    meals = []
    for day in range(num_days):
        delta = datetime.timedelta(days=day)
        for meal in Meal:
            meals.append(get_meal(start_day + delta, meal))
    return meals


def get_meal(day: datetime.date, meal: Meal):
    return get_cached_meal(day, meal) or get_online_meal(day, meal)


CACHE = xdg.xdg_cache_home() / "rofi-cafmenu"
CACHE.mkdir(parents=True, exist_ok=True)


def get_file(day: datetime.date, meal: Meal):
    return CACHE / f"{day.isoformat()}-{meal.name}.json"


def get_cached_meal(day: datetime.date, meal: Meal):
    try:
        with open(get_file(day, meal), "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return None


API_URL = "https://carleton.campusdish.com/api/menu/GetMenus"
PARAMS = "?locationId=5087&storeIds=&mode=Daily&date={}/{}/{}&time=&periodId={}&fulfillmentMethod="


def get_online_meal(day: datetime.date, meal: Meal):
    meal_data = requests.get(API_URL + PARAMS.format(day.month, day.day, day.year, meal.value)).json()
    with open(get_file(day, meal), "w") as file:
        json.dump(meal_data, file)
    return meal_data


class MealMenu(rofi_menu.Menu):
    prompt = "Meals"


class DishMenu(rofi_menu.Menu):
    prompt = "Dishes"


if __name__ == "__main__":
    get_meals(datetime.date.today(), 3)
    # rofi_menu.run(MealMenu(), rofi_version="1.6")
