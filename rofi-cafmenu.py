#!/home/mbradley/dev/rofi-cafmenu/venv/bin/python
import rofi_menu

import rofi_menus


if __name__ == "__main__":
    rofi_menu.run(rofi_menus.MealMenu(), rofi_version="1.6")
