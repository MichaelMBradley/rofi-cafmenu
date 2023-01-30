#!/home/mbradley/dev/rofi-cafmenu/venv/bin/python
import datetime

import caf_menu

if __name__ == "__main__":
    print(caf_menu.get_menus(datetime.datetime.now(), 7))
