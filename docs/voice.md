# Голос JARVIS

## Офлайн (по умолчанию) — ближе к киношному

Используется **Piper** — локальная нейросеть:

| Ключ | Модель | Характер |
|------|--------|----------|
| `jarvis_en` | `en_GB-alan-medium` | Британский мужской, спокойный «butler» |
| `jarvis_ru` | `ru_RU-dmitri-medium` | Русский мужской neural |

Модели (~60 МБ каждая) скачиваются **один раз** в `data/tts_models/`.
После этого интернет **не нужен**.

> Это не голос Пола Беттани из MCU (права Disney/Marvel).
> Это лучший бесплатный офлайн-аналог: британский мужской neural-тон.

## Приоритет (engine: auto)

1. **Piper** — офлайн neural  
2. **pyttsx3** — голоса Windows  
3. **edge-tts** — онлайн Microsoft (если Piper недоступен)

## Настройка

```yaml
tts:
  engine: auto    # auto | piper | offline | edge | pyttsx3
  voice: jarvis   # jarvis | jarvis_en | jarvis_ru
  rate: 160
  volume: 0.9
```

Только офлайн:

```yaml
tts:
  engine: piper
  voice: jarvis_en
```
