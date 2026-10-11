import tempfile
from pathlib import Path

from jarvis.memory.sqlite_store import MemoryStore


def test_memory_roundtrip():
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "test.db"
        store = MemoryStore(str(db))
        store.add_message("user", "hello")
        store.add_message("assistant", "hi there")
        recent = store.get_recent(10)
        assert len(recent) == 2
        assert recent[0]["role"] == "user"
        assert recent[1]["content"] == "hi there"


def test_facts():
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "test.db"
        store = MemoryStore(str(db))
        store.set_fact("name", "Alex")
        assert store.get_fact("name") == "Alex"
        assert store.get_fact("missing") is None
