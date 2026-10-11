# JARVIS v0.2

Локальный AI-ассистент в стиле **Luxify**: голос, сценарии, плагины, мульти-AI, Windows-управление.

## Возможности

| Модуль | Статус |
|--------|--------|
| 🇷🇺 / 🇬🇧 i18n | ✅ |
| Голос + обычный чат | ✅ |
| Wake word «Джарвис» / Jarvis | ✅ (STT-based) |
| Offline STT (Vosk) | ✅ если указан model path |
| AI: OpenAI / Gemini / Claude / Grok / DeepSeek / Ollama | ✅ |
| Плагины | ✅ auto-load |
| Редактор команд + сценарии | ✅ |
| Импорт / экспорт JSON | ✅ |
| Windows / браузер / файлы | ✅ |
| Steam / Discord / GitHub | ✅ stubs |
| Vision (screenshot) | ✅ |
| Память SQLite | ✅ |
| Системный монитор | ✅ |
| HUD overlay | ✅ |
| Подтверждение опасных действий | ✅ |

## Установка

```bash
git clone https://github.com/G1drohz/Jarvis.git
cd Jarvis
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt

# Микрофон (Windows):
pip install pipwin && pipwin install pyaudio
# Опционально клавиши:
pip install pyautogui

python -m jarvis.main
```

## AI-ключи (env)

```
OPENAI_API_KEY=
GEMINI_API_KEY=
ANTHROPIC_API_KEY=
XAI_API_KEY=
DEEPSEEK_API_KEY=
```

В `config/default.yaml`: `ai.provider: openai|gemini|claude|grok|deepseek|ollama|stub`

Ollama: локально `ollama serve`, provider `ollama`.

## Offline STT (Vosk)

1. Скачай модель: https://alphacephei.com/vosk/models  
2. В `config/default.yaml`:
```yaml
stt:
  engine: vosk
  vosk_model_path: "C:/models/vosk-model-small-ru"
```

## Голос

- **🎤** — одноразовое распознавание
- **Wake word** — непрерывный режим, фраза «джарвис …»
- Сценарии: «открой блокнот», «открой ютуб», «сделай громче»

## Структура

```
jarvis/
  ai/           # multi-provider
  scenarios/    # Luxify-style commands
  plugins/      # auto-load .py
  tools/        # windows, browser, files
  integrations/ # steam, discord, github
  voice/        # STT/TTS/wake
  vision/       # screenshot
  monitor/      # CPU/RAM
  ui/           # Luxify UI + HUD
  safety/       # confirmations
  i18n/         # ru/en
```

MIT
