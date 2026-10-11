"""Simple RU/EN i18n."""

from __future__ import annotations

from config.settings import settings

_STRINGS: dict[str, dict[str, str]] = {
    "ru": {
        "app.ready": "{name} готов. Нажми 🎤 или скажи «{wake}».",
        "nav.home": "🏠  Home",
        "nav.commands": "⚡  Команды",
        "nav.ai": "✦  JARVIS AI",
        "nav.monitor": "📊  Монитор",
        "nav.plugins": "🧩  Плагины",
        "nav.settings": "⚙  Настройки",
        "home.title": "Home",
        "home.sub": "Голос · чат · история",
        "home.history": "История",
        "home.chat": "Диалог",
        "home.placeholder": "Напиши или скажи «{wake}»…",
        "home.send": "Отправить",
        "home.clear": "Очистить",
        "home.speak": "Озвучивать ответы",
        "home.silent": "Silent",
        "home.ontop": "Always on top",
        "home.wake": "Wake word",
        "cmds.title": "Команды",
        "cmds.sub": "Коллекции · сценарии · импорт/экспорт",
        "cmds.collections": "Коллекции",
        "cmds.editor": "Редактор сценария",
        "cmds.phrase": "Фраза / триггер",
        "cmds.actions": "Действия (по одному на строку)",
        "cmds.save": "Сохранить",
        "cmds.run": "Запустить",
        "cmds.export": "Экспорт",
        "cmds.import": "Импорт",
        "cmds.ai": "✦ Создать с AI",
        "ai.title": "JARVIS AI",
        "ai.sub": "Мульти-провайдер: OpenAI · Gemini · Claude · Grok · DeepSeek · Ollama",
        "mon.title": "Системный монитор",
        "mon.sub": "CPU · RAM · диск · процессы",
        "pl.title": "Плагины",
        "pl.sub": "Подключаемые модули",
        "set.title": "Настройки",
        "set.sub": "Язык · AI · голос · безопасность",
        "voice.listening": "Слушаю…",
        "voice.wake": "Wake word активен",
        "voice.calibrating": "Калибровка…",
        "voice.recognizing": "Распознаю…",
        "confirm.title": "Подтверждение",
        "confirm.body": "Опасное действие: {action}\n\nПродолжить?",
        "confirm.yes": "Да",
        "confirm.no": "Отмена",
        "status.online": "Online",
        "you": "Ты",
        "system": "Система",
    },
    "en": {
        "app.ready": "{name} ready. Press 🎤 or say «{wake}».",
        "nav.home": "🏠  Home",
        "nav.commands": "⚡  Commands",
        "nav.ai": "✦  JARVIS AI",
        "nav.monitor": "📊  Monitor",
        "nav.plugins": "🧩  Plugins",
        "nav.settings": "⚙  Settings",
        "home.title": "Home",
        "home.sub": "Voice · chat · history",
        "home.history": "History",
        "home.chat": "Chat",
        "home.placeholder": "Type or say «{wake}»…",
        "home.send": "Send",
        "home.clear": "Clear",
        "home.speak": "Speak replies",
        "home.silent": "Silent",
        "home.ontop": "Always on top",
        "home.wake": "Wake word",
        "cmds.title": "Commands",
        "cmds.sub": "Collections · scenarios · import/export",
        "cmds.collections": "Collections",
        "cmds.editor": "Scenario editor",
        "cmds.phrase": "Phrase / trigger",
        "cmds.actions": "Actions (one per line)",
        "cmds.save": "Save",
        "cmds.run": "Run",
        "cmds.export": "Export",
        "cmds.import": "Import",
        "cmds.ai": "✦ Create with AI",
        "ai.title": "JARVIS AI",
        "ai.sub": "Providers: OpenAI · Gemini · Claude · Grok · DeepSeek · Ollama",
        "mon.title": "System monitor",
        "mon.sub": "CPU · RAM · disk · processes",
        "pl.title": "Plugins",
        "pl.sub": "Loadable modules",
        "set.title": "Settings",
        "set.sub": "Language · AI · voice · safety",
        "voice.listening": "Listening…",
        "voice.wake": "Wake word active",
        "voice.calibrating": "Calibrating…",
        "voice.recognizing": "Recognizing…",
        "confirm.title": "Confirm",
        "confirm.body": "Dangerous action: {action}\n\nContinue?",
        "confirm.yes": "Yes",
        "confirm.no": "Cancel",
        "status.online": "Online",
        "you": "You",
        "system": "System",
    },
}

_lang = settings.app.language if settings.app.language in _STRINGS else "ru"


def set_language(lang: str) -> None:
    global _lang
    if lang in _STRINGS:
        _lang = lang


def get_language() -> str:
    return _lang


def t(key: str, **kwargs) -> str:
    table = _STRINGS.get(_lang) or _STRINGS["ru"]
    text = table.get(key) or _STRINGS["en"].get(key) or key
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text
