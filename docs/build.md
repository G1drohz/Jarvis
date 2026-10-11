# Сборка приложения Windows

## Быстро

```bat
packaging\build.bat
```

Результат: `dist\JARVIS\JARVIS.exe` — можно запускать без Python.

## Установщик (.exe Setup)

1. Установи [Inno Setup 6](https://jrsoftware.org/isinfo.php)
2. Собери приложение: `packaging\build.bat`
3. Открой `packaging\installer.iss` в Inno Setup → **Compile**
4. Готовый установщик: `dist\installer\JARVIS-Setup-0.2.1.exe`

Установщик:
- ставит в `%LocalAppData%\Programs\JARVIS` (без админа) или Program Files
- ярлык в меню Пуск
- опционально: рабочий стол + автозапуск
- русский / English мастер

## Требования для сборки

- Windows 10/11
- Python 3.10+
- `pip install pyinstaller Pillow` + `requirements.txt`
- для установщика: Inno Setup 6

## Структура после сборки

```
dist/JARVIS/
  JARVIS.exe
  config/
  data/
  _internal/     # runtime libs
```

Данные пользователя (память, команды) пишутся в `data/` рядом с exe.
