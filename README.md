# Dynamics-Theme
__Dynamics Theme__ - это мини-приложение, которое запускается в трее и изменяет тему Windows. У него есть три варианта темы:

* Автоматическая
* Тёмная
* Светлая
> Автоматическая тема работает только при наличии интернета на устройстве.

### Используемые библиотеки:
```
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
```
