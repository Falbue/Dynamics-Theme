app_name = 'Dynamics Theme'
version = '1.2'

import ctypes
import pystray
from PIL import Image
import winreg
import requests
import ephem
import pytz
from datetime import datetime, timezone
import threading
import time
import os

def set_windows_theme(theme): # изменение темы
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", 0, winreg.KEY_WRITE) as key:
            if theme == "light":
                winreg.SetValueEx(key, "AppsUseLightTheme", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "SystemUsesLightTheme", 0, winreg.REG_DWORD, 1)
                icon.icon = Image.open("lib/icon_light.png")  # Изменяем иконку на светлую
            elif theme == "dark":
                winreg.SetValueEx(key, "AppsUseLightTheme", 0, winreg.REG_DWORD, 0)
                winreg.SetValueEx(key, "SystemUsesLightTheme", 0, winreg.REG_DWORD, 0)
                icon.icon = Image.open("lib/icon_dark.png")  # Изменяем иконку на тёмную
            else:
                print("Некорректная тема. Выберите 'light' или 'dark'.")
                return False
        return True
    except Exception as e:
        print("Ошибка при установке темы:", e)
        return False

def get_current_theme(): # получение текущей темы
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", 0, winreg.KEY_READ) as key:
            current_theme = winreg.QueryValueEx(key, "AppsUseLightTheme")[0]
        return current_theme
    except Exception as e:
        print("Ошибка при получении текущей темы:", e)
        return None

def get_location(): # получение координат
    try:
        response = requests.get('https://ipinfo.io/json')
        response.raise_for_status()
        data = response.json()
        latitude, longitude = map(float, data['loc'].split(','))
        return latitude, longitude
    except Exception as e:
        print("Ошибка при получении координат:", e)
        return None, None

def get_sunrise_and_sunset(latitude, longitude): # получение восхода и захода солнца
    try:
        observer = ephem.Observer()
        observer.lat, observer.lon = str(latitude), str(longitude)
        sunrise_time_utc = observer.next_rising(ephem.Sun()).datetime()
        sunset_time_utc = observer.next_setting(ephem.Sun()).datetime()
        return sunrise_time_utc, sunset_time_utc
    except Exception as e:
        print("Ошибка при определении времени восхода и захода солнца:", e)
        return None, None

def sun_time_local(sunrise_datetime_utc, sunset_datetime_utc): # локальное время восхода солнца
    try:
        local_offset = datetime.now(timezone.utc).astimezone().utcoffset()
        sunrise_time_local = sunrise_datetime_utc + local_offset
        sunset_time_local = sunset_datetime_utc + local_offset
        return sunrise_time_local.strftime('%H:%M:%S'), sunset_time_local.strftime('%H:%M:%S')
    except Exception as e:
        print("Ошибка при получении локального времени восхода и захода солнца:", e)
        return None, None

def automatic_data(): # объединение функций
    latitude, longitude = get_location()
    if latitude is None or longitude is None:
        return None
    
    sunrise_datetime_utc, sunset_datetime_utc = get_sunrise_and_sunset(latitude, longitude)
    if sunrise_datetime_utc is None or sunset_datetime_utc is None:
        return None

    return sun_time_local(sunrise_datetime_utc, sunset_datetime_utc)

def get_local_time(): # получение местного времени
    local_time = datetime.now().strftime("%H:%M:%S")
    return local_time

def select_theme(theme):
    stop_event.set()
    if theme == 'auto':
        start_automatic()
    else:
        print("Автомтический режим выключен")
        set_windows_theme(theme)

def start_automatic():
    print("Автомтический режим включен")
    global stop_event
    stop_event = threading.Event()
    thread = threading.Thread(target=automatic_theme)
    thread.start()

def automatic_theme():
    sunrise, sunset = automatic_data()
    if sunrise is None or sunset is None:
        print("Не удалось получить данные для автоматического режима")
        return
    
    while not stop_event.is_set():
        local_time = get_local_time()
        print(f"Восход: {sunrise}\nТекущее время: {local_time}\nЗаход: {sunset}")
        if sunrise < local_time < sunset:
            set_windows_theme("light")
        else:
            set_windows_theme("dark")
        time.sleep(60)

def create_tray_icon(): # создание меню трея
    global icon
    current_theme = get_current_theme()
    if current_theme is None:
        return
    
    icon = pystray.Icon("example", Image.open(f"lib/icon_{'light' if current_theme else 'dark'}.png"), app_name)
        
    menu_items = [
        pystray.MenuItem("Тёмная ☾", lambda: select_theme('dark')),
        pystray.MenuItem("Светлая ☼", lambda: select_theme('light')),
        pystray.MenuItem("Автоматическая", lambda: select_theme('auto')),
        pystray.MenuItem("Закрыть", lambda: hide_icon())
    ]
    
    icon.menu = pystray.Menu(*menu_items)
    start_automatic()
    icon.run()

def hide_icon():
    icon.stop()
    os._exit(0)

create_tray_icon()