from collections.abc import Iterable

from src.models.aeroplane import Aeroplane
from src.storage.base import AbstractAeroplaneStorage, Criteria

_NOT_READY = "Подключение к базе данных ещё не реализовано"


class DatabaseAeroplaneStorage(AbstractAeroplaneStorage):
    """Заглушка под коннектор к БД (SQLite, PostgreSQL и т.п.).

    Чтобы подключить БД, реализуй эти методы через SQL-запросы.
    Файлы service.py и ui.py при этом менять не придётся.
    """

    def add_aeroplanes(self, aeroplanes: Iterable[Aeroplane]) -> None:
        raise NotImplementedError(_NOT_READY)

    def get_aeroplanes(self, criteria: Criteria | None = None) -> list[Aeroplane]:
        raise NotImplementedError(_NOT_READY)

    def delete_aeroplanes(self, criteria: Criteria) -> int:
        raise NotImplementedError(_NOT_READY)

    def close(self) -> None:
        raise NotImplementedError(_NOT_READY)
