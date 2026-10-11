# JARVIS v0.2.1

Локальный AI-ассистент для Windows в стиле **Luxify Assistant**.

## Скачать

**https://github.com/G1drohz/Jarvis/releases/latest**

| Файл | Для кого |
|------|----------|
| **JARVIS-Setup-0.2.1.zip** | Установщик: сам поставит Python + зависимости + ярлыки |
| **JARVIS-Portable-0.2.1.zip** | Готовый `JARVIS.exe` без Python |

### Установка через Setup

1. Скачай `JARVIS-Setup-0.2.1.zip`
2. Распакуй
3. Запусти **`setup.bat`**
4. Дождись окончания → ярлык **JARVIS** на рабочем столе

### Portable

Распакуй и запусти `JARVIS.exe`.

## Разработка

```bash
git clone https://github.com/G1drohz/Jarvis.git
cd Jarvis
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m jarvis.main
```

MIT
