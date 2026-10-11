"""JSON store for command collections / scenarios."""

from __future__ import annotations

import json
import uuid
from pathlib import Path

from config.settings import settings
from jarvis.scenarios.models import Action, Collection, Scenario


DEFAULT_DATA = {
    "collections": [
        {
            "id": "windows",
            "name": "Windows",
            "scenarios": [
                {
                    "id": "vol_up",
                    "name": "Громче / Volume up",
                    "phrase": "сделай громче",
                    "aliases": ["turn it up", "volume up", "громче"],
                    "actions": [{"type": "key", "value": "volumeup"}],
                },
                {
                    "id": "vol_down",
                    "name": "Тише / Volume down",
                    "phrase": "сделай тише",
                    "aliases": ["turn it down", "volume down", "тише"],
                    "actions": [{"type": "key", "value": "volumedown"}],
                },
                {
                    "id": "notepad",
                    "name": "Блокнот",
                    "phrase": "открой блокнот",
                    "aliases": ["open notepad", "блокнот"],
                    "actions": [{"type": "launch", "value": "notepad.exe"}],
                },
            ],
        },
        {
            "id": "browser",
            "name": "Browser",
            "scenarios": [
                {
                    "id": "youtube",
                    "name": "YouTube",
                    "phrase": "открой ютуб",
                    "aliases": ["open youtube", "youtube"],
                    "actions": [{"type": "url", "value": "https://youtube.com"}],
                }
            ],
        },
        {"id": "custom", "name": "Custom", "scenarios": []},
    ]
}


class ScenarioStore:
    def __init__(self, path: str | None = None) -> None:
        self.path = Path(path or settings.commands.store_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.collections: list[Collection] = []
        self.load()

    def load(self) -> None:
        if not self.path.exists():
            self.collections = [Collection(**c) for c in DEFAULT_DATA["collections"]]
            self.save()
            return
        data = json.loads(self.path.read_text(encoding="utf-8"))
        self.collections = [Collection(**c) for c in data.get("collections", [])]

    def save(self) -> None:
        payload = {
            "collections": [c.model_dump() for c in self.collections],
        }
        self.path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def export(self, dest: Path) -> None:
        dest.write_text(
            json.dumps(
                {"collections": [c.model_dump() for c in self.collections]},
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    def import_file(self, src: Path, merge: bool = True) -> int:
        data = json.loads(src.read_text(encoding="utf-8"))
        incoming = [Collection(**c) for c in data.get("collections", [])]
        if not merge:
            self.collections = incoming
            self.save()
            return sum(len(c.scenarios) for c in incoming)
        # merge by id
        by_id = {c.id: c for c in self.collections}
        count = 0
        for col in incoming:
            if col.id not in by_id:
                by_id[col.id] = col
                count += len(col.scenarios)
            else:
                existing_ids = {s.id for s in by_id[col.id].scenarios}
                for sc in col.scenarios:
                    if sc.id not in existing_ids:
                        by_id[col.id].scenarios.append(sc)
                        count += 1
        self.collections = list(by_id.values())
        self.save()
        return count

    def find_by_phrase(self, text: str) -> Scenario | None:
        t = text.strip().lower()
        for col in self.collections:
            for sc in col.scenarios:
                if not sc.enabled:
                    continue
                phrases = [sc.phrase.lower()] + [a.lower() for a in sc.aliases]
                for p in phrases:
                    if p and (t == p or p in t or t in p):
                        return sc
        return None

    def add_scenario(self, collection_id: str, scenario: Scenario) -> None:
        for col in self.collections:
            if col.id == collection_id:
                col.scenarios.append(scenario)
                self.save()
                return
        # create collection
        self.collections.append(
            Collection(id=collection_id, name=collection_id, scenarios=[scenario])
        )
        self.save()

    def new_id(self) -> str:
        return uuid.uuid4().hex[:10]
