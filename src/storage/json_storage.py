import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from src.models.aeroplane import Aeroplane
from src.storage.base import AbstractAeroplaneStorage, Criteria


class JSONAeroplaneStorage(AbstractAeroplaneStorage):
    """Хранит самолёты в JSON-файле. Файл открывается только на время операции."""

    def __init__(self, path: str | Path = "data/aeroplanes.json") -> None:
        self.path = Path(path)

    def _read_rows(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        text = self.path.read_text(encoding="utf-8").strip()
        if not text:
            return []
        return json.loads(text)

    def _write_rows(self, rows: list[dict[str, Any]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        text = json.dumps(rows, ensure_ascii=False, indent=2)
        self.path.write_text(text, encoding="utf-8")

    def add_aeroplanes(self, aeroplanes: Iterable[Aeroplane]) -> None:
        rows = self._read_rows()
        rows.extend(plane.to_dict() for plane in aeroplanes)
        self._write_rows(rows)

    def get_aeroplanes(self, criteria: Criteria | None = None) -> list[Aeroplane]:
        planes = [Aeroplane.from_dict(row) for row in self._read_rows()]
        if criteria is None:
            return planes
        return [plane for plane in planes if criteria(plane)]

    def delete_aeroplanes(self, criteria: Criteria) -> int:
        rows = self._read_rows()
        kept = [row for row in rows if not criteria(Aeroplane.from_dict(row))]
        self._write_rows(kept)
        return len(rows) - len(kept)

    def close(self) -> None:
        # Заглушка: файл открывается и закрывается внутри каждой операции,
        # поэтому хранить открытое соединение не нужно.
        pass
