# JARVIS v0.2.1

Локальный AI-ассистент для Windows в стиле **Luxify Assistant**.

Готовый **desktop-app** с установщиком, треем, HUD, голосом и сценариями.

## Установка из исходников (разработка)

```bash
git clone https://github.com/G1drohz/Jarvis.git
cd Jarvis
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install pipwin && pipwin install pyaudio   # микрофон
python -m jarvis.main
```

## Сборка .exe + установщик

```bat
packaging\build.bat
```

Получишь `dist\JARVIS\JARVIS.exe`.

Установщик (Inno Setup 6):
1. Установи [Inno Setup](https://jrsoftware.org/isinfo.php)
2. Открой `packaging\installer.iss` → Compile
3. Файл: `dist\installer\JARVIS-Setup-0.2.1.exe`

Подробнее: [docs/build.md](docs/build.md)

## Возможности

- UI как у Luxify: сайдбар (сворачивается), Home, Commands, AI, Monitor, Plugins, Settings
- Системный трей (закрытие → в трей)
- Голос + wake word «Джарвис»
- Редактор сценариев + импорт/экспорт
- AI: OpenAI / Gemini / Claude / Grok / DeepSeek / Ollama
- Windows / браузер / файлы, HUD, монитор, безопасность

MIT
