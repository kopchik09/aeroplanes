from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable

from src.models.aeroplane import Aeroplane

# Критерий: функция, которая получает самолёт и возвращает True, если он подходит
Criteria = Callable[[Aeroplane], bool]


class AbstractAeroplaneStorage(ABC):
    """Контракт хранилища. Любой коннектор (JSON, CSV, БД) обязан реализовать эти методы."""

    @abstractmethod
    def add_aeroplanes(self, aeroplanes: Iterable[Aeroplane]) -> None:
        """Сохраняет самолёты в хранилище."""

    def add_aeroplane(self, aeroplane: Aeroplane) -> None:
        """Сохраняет один самолёт. Готовая реализация через add_aeroplanes."""
        self.add_aeroplanes([aeroplane])

    @abstractmethod
    def get_aeroplanes(self, criteria: Criteria | None = None) -> list[Aeroplane]:
        """Возвращает самолёты, подходящие под критерий. Без критерия возвращает все."""

    @abstractmethod
    def delete_aeroplanes(self, criteria: Criteria) -> int:
        """Удаляет самолёты, подходящие под критерий. Возвращает количество удалённых."""

    @abstractmethod
    def close(self) -> None:
        """Закрывает соединение с хранилищем."""
