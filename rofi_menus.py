import calendar
import datetime

import rofi_menu

import caf_menu
import data
import dates


MEAL_END_HOURS = {
    data.Meal.BREAKFAST: 11,
    data.Meal.LUNCH: 16,
    data.Meal.DINNER: 22,
}
"""The end times for the Caf meals."""


class MealMenu(rofi_menu.Menu):
    """A menu to display a list of submenus, one for each upcoming meal."""
    prompt = "Meals"

    def __init__(self, num_days: int = 3, **kwargs):
        """Creates submenus for breakfast, lunch, and dinner for the next `num_days` days."""
        super().__init__(**kwargs)

        self.items = []
        now = datetime.datetime.now()

        for day in dates.iter_days(datetime.datetime.today(), num_days):
            for meal in data.Meal:
                # If the meal is already over, skip it
                if now > dates.get_hour(now, MEAL_END_HOURS[meal]):
                    continue

                # If there was some problem getting the menu, skip it
                menu = caf_menu.get_menu(day, meal, False)
                if not menu:
                    continue

                # Add a new submenu to the list of items
                self.items.append(
                    rofi_menu.NestedMenu(
                        text=calendar.day_abbr[day.weekday()] + " " + meal.name.lower().capitalize(),
                        menu=StationMenu(menu=menu)
                    )
                )


class StationMenu(rofi_menu.Menu):
    """A menu to display the meals available at each station."""
    prompt = "Stations"

    def __init__(self, menu: caf_menu.Menu = None, **kwargs):
        super().__init__(**kwargs)

        # If there is some problem with the menu, skip it
        if menu is None:
            return

        # Start with the option to go back
        self.items = [rofi_menu.BackItem()]

        # For each station, get its name and list of meals
        for (station, meals) in menu.stations.items():
            # For each meal, add a listing containing its station and name
            for meal in meals:
                self.items.append(
                    rofi_menu.Item(
                        f"{station}: {meal}"
                    )
                )
