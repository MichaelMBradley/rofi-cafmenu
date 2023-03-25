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

    def __init__(self, num_days: int = 7, **kwargs):
        """Creates submenus for breakfast, lunch, and dinner for the next `num_days` days."""
        super().__init__(**kwargs)

        self.items = []
        now = datetime.datetime.now()

        for day in dates.iter_days(datetime.datetime.today(), num_days):
            for meal in data.Meal:
                # If the meal is ignored or already over, skip it
                if meal.name in data.ignored_meals() or now > dates.get_hour(day, MEAL_END_HOURS[meal]):
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

        # FIXME: Extract to function,
        #  add configuration to use old method,
        #  add configuration to split on words rather than meals
        # For each station, get its name and list of meals
        for (station, dishes) in menu.stations.items():
            # Add each meal to its row, creating a new row when it gets too long
            if station in data.ignored_stations():
                continue
            lines = [station + ": "]
            initial_offset = len(lines[0])
            for dish in dishes:
                if dish in data.ignored_dishes():
                    continue
                if len(lines[-1]) + len(dish) + 3 > data.MAX_LINE_LENGTH:
                    lines[-1] = lines[-1] + ","
                    lines.append(" " * (initial_offset - 4) + "└ : ")
                if len(lines[-1]) == initial_offset:
                    lines[-1] = lines[-1] + dish
                else:
                    lines[-1] = lines[-1] + ", " + dish
            for line in lines:
                self.items.append(rofi_menu.Item(line))
