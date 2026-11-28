from abc import ABC, abstractmethod
from typing import Any

# Прямоугольник: (южная широта, северная широта, западная долгота, восточная долгота)
BBox = tuple[float, float, float, float]


class APIError(Exception):
    """Любая ошибка при работе с внешним сервисом: сеть, HTTP-код, неверный ответ."""


class CountryNotFoundError(APIError):
    """Страна не найдена в Nominatim."""


class AbstractAPIAdapter(ABC):
    """Общий интерфейс для адаптеров сервисов Nominatim и OpenSky.

    Класс не содержит сетевой логики. Он описывает,
    какие методы должен предоставить любой адаптер.
    """

    @abstractmethod
    def get_country_bbox(self, country: str) -> BBox:
        """Возвращает координаты прямоугольника, в который попадает страна."""

    @abstractmethod
    def get_aeroplanes_in_bbox(self, bbox: BBox) -> list[list[Any]]:
        """Возвращает сырые состояния самолётов внутри прямоугольника."""

    def get_aeroplanes(self, country: str) -> list[list[Any]]:
        """Шаблонный метод: сначала границы страны, затем самолёты в этих границах."""
        bbox = self.get_country_bbox(country)
        return self.get_aeroplanes_in_bbox(bbox)
