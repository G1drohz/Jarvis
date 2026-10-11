# Голос JARVIS

## TTS (речь)

По умолчанию `tts.engine: auto`:

1. **edge-tts** — нейросеть Microsoft (бесплатно, без ключа)
   - `voice: jarvis` → RU Dmitry / EN Ryan (GB)
2. **pyttsx3** — офлайн запас (голоса Windows)

### Настройка (`config/default.yaml`)

```yaml
tts:
  enabled: true
  engine: auto   # auto | edge | pyttsx3 | stub
  voice: jarvis  # jarvis | jarvis_en | jarvis_ru | male_en | ...
  volume: 0.9
```

Для озвучки edge-tts нужен интернет.
