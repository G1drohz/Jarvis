# Getting Started

## Требования

- Python 3.10+
- Windows рекомендуется (есть Windows-tools), но код кроссплатформенный.

## Установка

```bash
git clone https://github.com/G1drohz/Jarvis.git
cd Jarvis
python -m venv .venv
.venv\\Scripts\\activate          # Windows
pip install -r requirements.txt
```

## Запуск

```bash
python -m jarvis.main
```

Откроется окно с тёмным интерфейсом.

## OpenAI (опционально)

```bash
set OPENAI_API_KEY=sk-...
```

Или пропиши ключ в `config/default.yaml` / через env.

В `config/default.yaml` поставь:

```yaml
ai:
  provider: openai
```

## Команды

- `help` / `помощь` — список команд
- `status` — статус
- `clear` — очистить историю
