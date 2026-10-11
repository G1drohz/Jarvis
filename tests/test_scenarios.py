from jarvis.scenarios.models import Action, Scenario
from jarvis.scenarios.store import ScenarioStore
import tempfile
from pathlib import Path


def test_find_phrase():
    with tempfile.TemporaryDirectory() as tmp:
        store = ScenarioStore(str(Path(tmp) / "c.json"))
        sc = store.find_by_phrase("открой блокнот")
        assert sc is not None
        assert sc.actions[0].type == "launch"


def test_export_import():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp)
        store = ScenarioStore(str(p / "c.json"))
        out = p / "export.json"
        store.export(out)
        n = store.import_file(out, merge=True)
        assert n >= 0
