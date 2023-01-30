#!/home/mbradley/dev/rofi-cafmenu/venv/bin/python
import pathlib
import subprocess

import rofi_menu

import rofi_menus


if __name__ == "__main__":
    cacher = pathlib.Path(__file__).parent / "cache-upcoming-meals.py"
    subprocess.Popen([cacher], stdout=subprocess.DEVNULL)
    rofi_menu.run(rofi_menus.MealMenu(), rofi_version="1.6")
