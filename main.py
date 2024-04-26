import ctypes
import pystray
from PIL import Image
import tkinter as tk
import winreg

app_name = 'Dynamics Theme'

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
