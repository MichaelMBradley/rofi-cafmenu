#!/home/mbradley/dev/rofi-cafmenu/venv/bin/python
import calendar
import datetime
import enum
import json

import requests
import rofi_menu
import xdg


class Meal(enum.Enum):
    BREAKFAST = 2082
    LUNCH = 2084
    DINNER = 2085


class Menu:
    def __init__(self, data):
        station_ids = {
            station["StationId"]: station["Name"]
            for station in data["Menu"]["MenuStations"]
            if station["PeriodId"] == data["SelectedPeriodId"]
        }
        self.stations = {name: [] for name in station_ids.values()}
        for food in data["Menu"]["MenuProducts"]:
            self.stations[station_ids[food["StationId"]]].append(food["Product"]["MarketingName"])


def iter_days(start_day: datetime.datetime, num_days: int):
    for i in range(num_days):
        yield start_day + datetime.timedelta(days=i)


def get_menus(start_day: datetime.datetime, num_days: int):
    meals = []
    for day in iter_days(start_day, num_days):
        for meal in Meal:
            meals.append(get_menu(day, meal))
    return meals


def get_menu(day: datetime.datetime, meal: Meal, synchronous: bool = True) -> Menu | None:
    menu = get_cached_menu(day, meal)
    if menu:
        return menu
    if synchronous:
        return get_online_menu(day, meal)


CACHE = xdg.xdg_cache_home() / "rofi-cafmenu"
CACHE.mkdir(parents=True, exist_ok=True)


def get_file(day: datetime.date, meal: Meal):
    return CACHE / f"{day.date().isoformat()}-{meal.name}.json"


def get_cached_menu(day: datetime.date, meal: Meal):
    try:
        with open(get_file(day, meal), "r") as file:
            return Menu(json.load(file))
    except FileNotFoundError:
        return None


API_URL = "https://carleton.campusdish.com/api/menu/GetMenus"
PARAMS = "?locationId=5087&storeIds=&mode=Daily&date={}/{}/{}&time=&periodId={}&fulfillmentMethod="


def get_online_menu(day: datetime.date, meal: Meal):
    menu_data = requests.get(API_URL + PARAMS.format(day.month, day.day, day.year, meal.value)).json()
    with open(get_file(day, meal), "w") as file:
        json.dump(menu_data, file)
    return Menu(menu_data)


class StationMenu(rofi_menu.Menu):
    prompt = "Stations"

    def __init__(self, menu: Menu = None, **kwargs):
        super().__init__(**kwargs)
        if menu is None:
            return
        self.items = [rofi_menu.BackItem()]
        for (station, items) in menu.stations.items():
            for item in items:
                self.items.append(
                    rofi_menu.Item(
                        f"{station}: {item}"
                    )
                )


MEAL_END_HOURS = {
    Meal.BREAKFAST: 11,
    Meal.LUNCH: 16,
    Meal.DINNER: 22,
}


class MealMenu(rofi_menu.Menu):
    prompt = "Meals"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.items = []
        now = datetime.datetime.now()
        for day in iter_days(datetime.datetime.today(), 3):
            for meal in Meal:
                if now > day.replace(hour=MEAL_END_HOURS[meal], minute=0, second=0, microsecond=0):
                    continue
                menu = get_menu(day, meal, False)
                if not menu:
                    continue
                self.items.append(
                    rofi_menu.NestedMenu(
                        text=calendar.day_abbr[day.weekday()] + " " + meal.name.lower().capitalize(),
                        menu=StationMenu(menu=menu)
                    )
                )


if __name__ == "__main__":
    rofi_menu.run(MealMenu(), rofi_version="1.6")
