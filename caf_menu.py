import datetime
import typing

import data
import dates


class Menu:
    """Basic class to help parse the JSON menus."""

    def __init__(self, json: typing.Any):
        """Retrieves the meals from the JSON menu data."""
        self.data = json
        station_ids = {
            station["StationId"]: station["Name"]
            for station in json["Menu"]["MenuStations"]
            if station["PeriodId"] == json["SelectedPeriodId"]
        }
        self.stations = {name: [] for name in station_ids.values()}
        for food in json["Menu"]["MenuProducts"]:
            self.stations[station_ids[food["StationId"]]].append(food["Product"]["MarketingName"])

    def __str__(self) -> str:
        return str(self.stations)

    def __repr__(self) -> str:
        # Strictly speaking, it should be:
        # return str(self.data)
        # But that makes readability way worse, so I'm bending the rules here
        return str(self)


def get_menus(start_day: datetime.datetime, num_days: int) -> list[Menu | None]:
    """Gets the 3 daily menus for `num_days` starting at `start_day`."""
    meals = []
    for day in dates.iter_days(start_day, num_days):
        for meal in data.Meal:
            meals.append(get_menu(day, meal))
    return meals


def get_menu(day: datetime.datetime, meal: data.Meal, fetch_online: bool = True) -> Menu | None:
    """Gets the menu for the specified day and meal.
    If the data is not stored locally and `fetch_online` is `False`, it returns None."""
    menu = data.get_cached_menu(day, meal)
    if menu:
        return Menu(menu)
    if fetch_online:
        return Menu(data.cache_menu(day, meal))
