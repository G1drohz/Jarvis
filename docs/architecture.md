# Архитектура JARVIS v0.1

## Обзор

JARVIS — модульный локальный ассистент.

```
UI (PySide6)
    ↓
Agent (core)
    ├── AI Provider (stub / OpenAI)
    ├── Command Registry
    ├── Memory (SQLite)
    ├── Permissions
    └── Tools / Plugins
```

## Поток сообщения

1. Пользователь вводит текст в UI (или console).
2. `Agent.process()` сначала пробует распознать команду.
3. Если команда не найдена — отправляет историю в AI-провайдер.
4. Ответ сохраняется в SQLite и показывается пользователю.

## Расширение

- Новые команды → `jarvis/commands/` + регистрация в `CommandRegistry`.
- Плагины → `jarvis/plugins/` (пока ручная регистрация).
- Новый AI → реализовать `AIProvider` и добавить в `get_provider`.
- STT / TTS / Vision — заменить stub-классы на реальные движки.
