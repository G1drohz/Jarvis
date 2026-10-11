# Architecture v0.2

```
UI (Luxify pages + HUD)
  ├── Voice (mic / wake word)
  └── Agent
        ├── Commands (text plugins)
        ├── Scenarios (phrase → multi-action)
        ├── AI providers (OpenAI-compatible, Gemini, Claude, Ollama)
        ├── Memory (SQLite)
        ├── Vision (screenshot)
        ├── Tools (Windows / browser / files)
        ├── Integrations (Steam / Discord / GitHub)
        ├── Plugins (discover + register)
        └── Safety (confirm dangerous actions)
```

## Scenario actions

| type | example |
|------|---------|
| launch | notepad.exe |
| url | https://youtube.com |
| key | volumeup |
| type | Hello |
| wait | 1 |
| open_path | C:\\Users |
| shell | echo hi |
| shutdown / restart | (needs confirm) |
| delete_file | (needs confirm) |

## Adding a plugin

Create `data/plugins/my_plugin.py`:

```python
def register(agent):
    # agent.commands.register(...)
    pass
```
