import rofi_menu
from xdg import xdg_cache_home

CACHE = xdg_cache_home() / "rofi-cafmenu"


class MealsMenu(rofi_menu.Menu):
    prompt = "Meals"
    items = [
        rofi_menu.TouchpadItem()
    ]


if __name__ == "__main__":
    print(CACHE.glob("*"))
    # rofi_menu.run(MealsMenu(), rofi_version="1.6")
