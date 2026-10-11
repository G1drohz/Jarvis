# Голосовое управление JARVIS

## Что умеет

- **STT** — распознавание речи с микрофона (Google Web Speech, язык `ru-RU`)
- **TTS** — озвучка ответов через системные голоса (pyttsx3 / SAPI5 на Windows)
- Кнопка **🎤** на Home: нажал → сказал → JARVIS ответил (и озвучил)
- Чекбокс «Озвучивать ответы» / Silent mode
- Громкость TTS слайдером

## Установка зависимостей

```bash
pip install SpeechRecognition pyttsx3
```

### PyAudio (микрофон)

**Windows (часто нужно так):**

```bash
pip install pipwin
pipwin install pyaudio
```

Или скачай wheel под свою версию Python:  
https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

**Linux:**

```bash
sudo apt install portaudio19-dev python3-pyaudio
pip install PyAudio
```

**macOS:**

```bash
brew install portaudio
pip install PyAudio
```

## Настройки (`config/default.yaml`)

```yaml
stt:
  enabled: true
  engine: google      # google | sphinx
  language: ru-RU
  phrase_time_limit: 8

tts:
  enabled: true
  engine: pyttsx3
  rate: 175
  volume: 0.9

voice:
  speak_replies: true
  wake_word: "джарвис"
  continuous: false   # пока не реализовано
```

Google STT требует интернет. Для полностью офлайн — позже можно добавить Vosk / Whisper.

## Как пользоваться

1. Запусти `python -m jarvis.main`
2. Разреши доступ к микрофону в Windows, если спросит
3. На Home нажми **🎤**, дождись «Слушаю…» и говори
4. Текст появится в чате, JARVIS ответит и (если включено) озвучит ответ

## Дальше

- Wake word («Джарвис, …») + continuous listening
- Vosk / faster-whisper offline STT
- Edge-TTS / ElevenLabs для голоса «Джарвиса»
