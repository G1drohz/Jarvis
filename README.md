# JARVIS

Локальный персональный AI-ассистент (**v0.1**).

Интерфейс в стиле **Luxify Assistant**: боковое меню, Home с историей и панелью управления, разделы Commands / AI / Settings, тёмная тема.

## Быстрый старт

```bash
git clone https://github.com/G1drohz/Jarvis.git
cd Jarvis

python -m venv .venv
# Windows
.venv\\Scripts\\activate
# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
python -m jarvis.main
```

## Что внутри

| Раздел UI | Содержимое |
|-----------|------------|
| **Home** | Чат, история команд, mic-кнопка, control panel (prefix / silent / avatar / always on top / volume) |
| **Commands** | Коллекции + черновик редактора команд (+ «Создать с AI») |
| **JARVIS AI** | Отдельный чат с выбором модели |
| **Settings** | Тема, язык, AI-провайдер, права, голос |

Под капотом: ядро агента, AI-абстракция (stub / OpenAI), команды, плагины, Windows-tools, SQLite-память, permissions, STT/TTS/Vision stubs, тесты, CI.

## OpenAI (опционально)

```bash
set OPENAI_API_KEY=sk-...
```

В `config/default.yaml`:

```yaml
ai:
  provider: openai
```

## Структура

```
jarvis/
├── core/          # агент
├── ai/            # провайдеры
├── commands/      # команды
├── plugins/
├── tools/windows/
├── memory/        # SQLite
├── permissions/
├── ui/            # Luxify-style UI
├── stt/ tts/ vision/   # stubs
```

## Тесты

```bash
pytest
```

## Дальше

Голос (wake word + STT/TTS), реальный редактор команд, HUD, Vision, управление Windows, Discord/Steam/GitHub.

MIT
