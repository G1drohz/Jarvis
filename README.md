# JARVIS

Локальный персональный AI-ассистент (**v0.1.1**).

Интерфейс в стиле **Luxify Assistant** + **голосовое управление** (STT + TTS).

## Быстрый старт

```bash
git clone https://github.com/G1drohz/Jarvis.git
cd Jarvis

python -m venv .venv
.venv\\Scripts\\activate          # Windows

pip install -r requirements.txt

# Микрофон (Windows):
pip install pipwin
pipwin install pyaudio

python -m jarvis.main
```

Нажми **🎤** на Home и говори.

## Возможности

| Раздел | Содержимое |
|--------|------------|
| **Home** | Чат, история, mic, озвучка ответов, always on top |
| **Commands** | Коллекции + черновик редактора |
| **JARVIS AI** | Отдельный чат с моделью |
| **Settings** | Статус STT/TTS, AI, права |

**Голос:** Google STT (`ru-RU`) + pyttsx3 TTS. Подробнее — [docs/voice.md](docs/voice.md).

## OpenAI (опционально)

```bash
set OPENAI_API_KEY=sk-...
```

В `config/default.yaml`: `ai.provider: openai`.

## Тесты

```bash
pytest
```

MIT
