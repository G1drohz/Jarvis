# JARVIS v0.2.1

Локальный AI-ассистент для Windows в стиле **Luxify Assistant**.

## Скачать (готово к запуску)

После сборки релиза:

**https://github.com/G1drohz/Jarvis/releases/latest**

1. Скачай `JARVIS-Portable-0.2.1.zip`
2. Распакуй
3. Запусти `JARVIS.exe`

Python **не нужен**.

Если Windows SmartScreen ругается: «Подробнее» → «Выполнить в любом случае».

## Сборка релиза (для разработчика)

```
GitHub → Actions → Build Windows Release → Run workflow
```

Или локально: `packaging\build.bat`

## Из исходников

```bash
git clone https://github.com/G1drohz/Jarvis.git
cd Jarvis
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m jarvis.main
```

MIT
