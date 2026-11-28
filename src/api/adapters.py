import requests

from src.api.base import AbstractAPIAdapter, APIError, BBox, CountryNotFoundError


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

    def _get_json(self, url: str, params: dict, headers: dict | None = None):
        """Единая точка для всех запросов: ошибки сети превращаются в APIError."""
        try:
            response = self.session.get(
                url, params=params, headers=headers, timeout=self.TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as error:
            raise APIError(f"Не удалось получить данные с {url}: {error}") from error

    def get_country_bbox(self, country: str) -> BBox:
        results = self._get_json(
            self.NOMINATIM_URL,
            params={"country": country, "format": "json", "limit": 1},
            headers=self.HEADERS,
        )
        if not results:
            raise CountryNotFoundError(f"Страна «{country}» не найдена")

        # boundingbox: южная, северная, западная, восточная. Значения приходят строками.
        south, north, west, east = (float(x) for x in results[0]["boundingbox"])
        return south, north, west, east

    def get_aeroplanes_in_bbox(self, bbox: BBox) -> list[list]:
        lamin, lamax, lomin, lomax = bbox
        data = self._get_json(
            self.OPENSKY_URL,
            params={"lamin": lamin, "lamax": lamax, "lomin": lomin, "lomax": lomax},
        )
        # states равно null, если над регионом нет самолётов
        return data.get("states") or []
