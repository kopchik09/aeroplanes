import requests

from src.api.base import AbstractAPIAdapter, BBox


class CountryNotFoundError(Exception):
    """Страна не найдена в Nominatim."""


class OpenSkyNominatimAdapter(AbstractAPIAdapter):
    """Адаптер, который работает с Nominatim и OpenSky."""

    NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
    OPENSKY_URL = "https://opensky-network.org/api/states/all"
    # Nominatim требует, чтобы запрос содержал User-Agent
    HEADERS = {"User-Agent": "aeroplanes-course-project/1.0"}
    TIMEOUT = 15  # секунд

    def __init__(self, session: requests.Session | None = None) -> None:
        # Сессию передаём извне, чтобы в тестах подменять её заглушкой
        self.session = session or requests.Session()

    def get_country_bbox(self, country: str) -> BBox:
        response = self.session.get(
            self.NOMINATIM_URL,
            params={"country": country, "format": "json", "limit": 1},
            headers=self.HEADERS,
            timeout=self.TIMEOUT,
        )
        response.raise_for_status()

        results = response.json()
        if not results:
            raise CountryNotFoundError(f"Страна «{country}» не найдена")

        # В boundingbox порядок: южная, северная, западная, восточная.
        # Значения приходят строками, поэтому приводим к float.
        south, north, west, east = (float(x) for x in results[0]["boundingbox"])
        return south, north, west, east

    def get_aeroplanes_in_bbox(self, bbox: BBox) -> list[list]:
        lamin, lamax, lomin, lomax = bbox
        response = self.session.get(
            self.OPENSKY_URL,
            params={"lamin": lamin, "lamax": lamax, "lomin": lomin, "lomax": lomax},
            timeout=self.TIMEOUT,
        )
        response.raise_for_status()

        # Поле states равно null, если над регионом нет самолётов
        return response.json().get("states") or []
