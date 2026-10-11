# JARVIS

Локальный персональный AI-ассистент (стартовая версия **v0.1**).

Рабочий фундамент: ядро агента, AI-абстракция, система команд, плагины, Windows-инструменты, SQLite-память, permissions, PySide6 UI, заготовки STT/TTS/Vision, тесты и CI.

> Это **не** финальная версия. Дальше можно наращивать: нормальный AI, голос «Джарвис», wake word, сценарии, HUD, Vision, браузер, Discord/Steam/GitHub и полноценное управление Windows.

## Быстрый старт

```bash
# Клонируй
git clone https://github.com/G1drohz/Jarvis.git
cd Jarvis

# Виртуальное окружение
python -m venv .venv
# Windows
.venv\\Scripts\\activate
# Linux/macOS
source .venv/bin/activate

# Зависимости
pip install -r requirements.txt

# Запуск
python -m jarvis.main
```

## Структура

```
jarvis/
├── core/          # ядро агента и главный цикл
├── ai/            # абстракция AI-провайдеров
├── commands/      # система команд
├── plugins/       # плагины
├── tools/windows/ # Windows-инструменты
├── memory/        # SQLite-память
├── permissions/   # права доступа
├── ui/            # PySide6 интерфейс
├── stt/           # Speech-to-Text (заготовка)
├── tts/           # Text-to-Speech (заготовка)
└── vision/        # Vision (заготовка)
```

## Конфигурация

Смотри `config/default.yaml` и `config/settings.py`.

## Тесты

```bash
pytest
```

## Лицензия

MIT
