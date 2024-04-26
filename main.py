app_name = 'Dynamics Theme'
version = '1.0'

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


def set_windows_theme(theme): # изменение темы
    try:
        # Открываем ключ реестра для тем
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", 0, winreg.KEY_WRITE)
        
        # Устанавливаем тему в соответствии с выбором
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
        
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print("Ошибка при установке темы:", e)
        return False

def get_current_theme(): # получение текущей темы
    try:
        # Открываем ключ реестра для текущей темы
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", 0, winreg.KEY_READ)
        # Получаем значение текущей темы
        current_theme = winreg.QueryValueEx(key, "AppsUseLightTheme")[0]
        winreg.CloseKey(key)
        # Возвращаем текущую тему (True для светлой, False для тёмной)
        return current_theme
    except Exception as e:
        print("Ошибка при получении текущей темы:", e)
        return None

def get_location(): # получение координат
    try:
        response = requests.get('https://ipinfo.io/json')
        data = response.json()
        coordinates = data['loc'].split(',')
        latitude = float(coordinates[0])
        longitude = float(coordinates[1])
        return latitude, longitude
    except Exception as e:
        print("Ошибка при получении координат:", e)
        return None, None

def get_sunrise_and_sunset(latitude, longitude): # получение восхода и захода солнца
    try:
        observer = ephem.Observer()
        observer.lat = str(latitude)
        observer.lon = str(longitude)
        
        sunrise_time_utc = observer.next_rising(ephem.Sun())
        sunset_time_utc = observer.next_setting(ephem.Sun())
        
        sunrise_datetime_utc = sunrise_time_utc.datetime()
        sunset_datetime_utc = sunset_time_utc.datetime()
        
        return sunrise_datetime_utc, sunset_datetime_utc
    except Exception as e:
        print("Ошибка при определении времени восхода и захода солнца:", e)
        return None, None

def sun_time_local(latitude, longitude, sunrise_datetime_utc, sunset_datetime_utc): # локальное время восхода солнца
    try:
        import datetime
        # Получаем смещение местного времени относительно UTC
        local_offset = datetime.datetime.now(datetime.timezone.utc).astimezone().utcoffset()

        # Применяем смещение к времени восхода и захода солнца
        sunrise_time_local = sunrise_datetime_utc + local_offset
        sunset_time_local = sunset_datetime_utc + local_offset

        # Преобразуем время в строковый формат
        sunrise = sunrise_time_local.strftime('%H:%M:%S')
        sunset = sunset_time_local.strftime('%H:%M:%S')

        return sunrise, sunset
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

    sunrise, sunset = sun_time_local(latitude, longitude, sunrise_datetime_utc, sunset_datetime_utc)
    if sunrise is None or sunset is None:
        return None
    else:
        print(f'Время восхода солнца: {sunrise}')
        print(f'Время захода солнца: {sunset}')
        return sunrise, sunset

def get_local_time(): # получение местного времени
    utc_time = datetime.now(timezone.utc) # Получаем текущее время в формате UTC
    local_offset = utc_time.astimezone().utcoffset() # Получаем смещение местного времени относительно UTC
    local_time = utc_time + local_offset # Добавляем смещение к текущему времени UTC, чтобы получить местное время
    local_time_formatted = local_time.strftime("%H:%M:%S") # Форматируем время в формат часов, минут и секунд
    return local_time_formatted

stop_event = threading.Event()
def non_automatic(theme):
    stop_event.set()
    set_windows_theme(theme)

def stop_theme():
    stop_event.set()

def start_automatic():
    # Создаем и запускаем поток
    thread = threading.Thread(target=automatic_theme)
    thread.start()
    
def automatic_theme():
    sunrise, sunset = automatic_data()
    while not stop_event.is_set():
        local_time = get_local_time()
        print(sunrise, local_time, sunset)
        # Проверяем, находимся ли мы в промежутке между восходом и заходом солнца
        if sunrise < local_time < sunset:
            set_windows_theme("light")  # Если да, выбираем светлую тему
        else:
            set_windows_theme("dark")   # Если нет, выбираем темную тему
        time.sleep(60)

def create_tray_icon(): # создание меню трея
    global icon  # Делаем иконку доступной везде в коде
    current_theme = get_current_theme()
    if current_theme is None:
        return
    
    if current_theme:
        icon = pystray.Icon("example", Image.open("lib/icon_light.png"), app_name)
    else:
        icon = pystray.Icon("example", Image.open("lib/icon_dark.png"), app_name)
        
    icon.menu = pystray.Menu( # кнопки в меню
        pystray.MenuItem("Тёмная", lambda: set_windows_theme('dark')),
        pystray.MenuItem("Светлая", lambda: set_windows_theme('light'))
    )
    icon.run()

# Создаем графический интерфейс
root = tk.Tk()
root.title(app_name)
root.geometry("300x150")

# Минимизируем окно в трей при запуске
root.withdraw()

# Запускаем приложение
root.after(0, create_tray_icon)

root.mainloop()
