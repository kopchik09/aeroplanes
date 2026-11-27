import math
import re
from collections.abc import Sequence
from typing import Any

# OpenSky отдаёт icao24 как 6 шестнадцатеричных символов, например "4b1812"
_ICAO24_PATTERN = re.compile(r"^[0-9a-f]{6}$")

# Границы высоты: ниже уровня Мёртвого моря и выше любого самолёта
MIN_ALTITUDE_M = -500.0
MAX_ALTITUDE_M = 30000.0


def _require_str(value: Any, name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} должен быть строкой, получено {type(value).__name__}")
    return value.strip()


def _require_number(value: Any, name: str) -> float:
    # bool — подкласс int, поэтому отсекаем его отдельно
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} должен быть числом, получено {type(value).__name__}")
    if not math.isfinite(value):
        raise ValueError(f"{name} должен быть конечным числом")
    return float(value)


def _compare(a: float, b: float) -> int:
    return (a > b) - (a < b)


class Aeroplane:
    """Самолёт из данных OpenSky.

    Атрибуты скрыты (имена начинаются с _). Читать их можно через свойства,
    менять только через свойства, которые проверяют значение.
    """

    __slots__ = (
        "_icao24",
        "_callsign",
        "_origin_country",
        "_velocity",
        "_baro_altitude",
        "_on_ground",
    )

    def __init__(
        self,
        callsign: str,
        origin_country: str,
        velocity: float,
        baro_altitude: float,
        on_ground: bool = False,
        icao24: str | None = None,
    ) -> None:
        self.callsign = callsign
        self.origin_country = origin_country
        self.velocity = velocity
        self.baro_altitude = baro_altitude
        self.on_ground = on_ground
        self.icao24 = icao24

    # ---------- свойства с проверкой ----------

    @property
    def icao24(self) -> str | None:
        return self._icao24

    @icao24.setter
    def icao24(self, value: str | None) -> None:
        if value is None:
            self._icao24 = None
            return
        value = _require_str(value, "icao24").lower()
        if not _ICAO24_PATTERN.match(value):
            raise ValueError(
                f"icao24 должен быть из 6 шестнадцатеричных символов, получено {value!r}"
            )
        self._icao24 = value

    @property
    def callsign(self) -> str:
        return self._callsign

    @callsign.setter
    def callsign(self, value: str) -> None:
        value = _require_str(value, "callsign")
        if not value:
            raise ValueError("callsign не может быть пустым")
        self._callsign = value

    @property
    def origin_country(self) -> str:
        return self._origin_country

    @origin_country.setter
    def origin_country(self, value: str) -> None:
        value = _require_str(value, "origin_country")
        if not value:
            raise ValueError("origin_country не может быть пустым")
        self._origin_country = value

    @property
    def velocity(self) -> float:
        return self._velocity

    @velocity.setter
    def velocity(self, value: float) -> None:
        value = _require_number(value, "velocity")
        if value < 0:
            raise ValueError("velocity не может быть отрицательной")
        self._velocity = value

    @property
    def baro_altitude(self) -> float:
        return self._baro_altitude

    @baro_altitude.setter
    def baro_altitude(self, value: float) -> None:
        value = _require_number(value, "baro_altitude")
        if not MIN_ALTITUDE_M <= value <= MAX_ALTITUDE_M:
            raise ValueError(
                f"baro_altitude должна быть от {MIN_ALTITUDE_M} до {MAX_ALTITUDE_M} м, получено {value}"
            )
        self._baro_altitude = value

    @property
    def on_ground(self) -> bool:
        return self._on_ground

    @on_ground.setter
    def on_ground(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise TypeError("on_ground должен быть True или False")
        self._on_ground = value

    # ---------- сравнение ----------

    @staticmethod
    def _check_other(other: object) -> None:
        if not isinstance(other, Aeroplane):
            raise TypeError("Сравнивать можно только два объекта Aeroplane")

    def compare_speed(self, other: "Aeroplane") -> int:
        """-1 если этот самолёт медленнее, 0 если скорости равны, 1 если быстрее."""
        self._check_other(other)
        return _compare(self._velocity, other._velocity)

    def compare_altitude(self, other: "Aeroplane") -> int:
        """-1 если этот самолёт ниже, 0 если на одной высоте, 1 если выше."""
        self._check_other(other)
        return _compare(self._baro_altitude, other._baro_altitude)

    def __lt__(self, other: object) -> bool:
        """Нужен для sorted(): самолёты упорядочиваются по высоте."""
        if not isinstance(other, Aeroplane):
            return NotImplemented
        return self._baro_altitude < other._baro_altitude

    # ---------- создание и преобразование ----------

    @classmethod
    def from_state(cls, state: Sequence[Any]) -> "Aeroplane":
        """Создаёт самолёт из массива states, который отдаёт OpenSky."""
        return cls(
            icao24=state[0],
            callsign=(state[1] or "").strip() or "UNKNOWN",
            origin_country=state[2] or "Unknown",
            baro_altitude=state[7] if state[7] is not None else 0.0,
            on_ground=bool(state[8]),
            velocity=state[9] if state[9] is not None else 0.0,
        )

    @classmethod
    def cast_to_object_list(cls, states: Sequence[Sequence[Any]]) -> list["Aeroplane"]:
        return [cls.from_state(state) for state in states]

    def to_dict(self) -> dict[str, Any]:
        return {
            "icao24": self.icao24,
            "callsign": self.callsign,
            "origin_country": self.origin_country,
            "velocity": self.velocity,
            "baro_altitude": self.baro_altitude,
            "on_ground": self.on_ground,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Aeroplane":
        return cls(**data)

    def __repr__(self) -> str:
        return (
            f"Aeroplane(callsign={self.callsign!r}, country={self.origin_country!r}, "
            f"velocity={self.velocity}, altitude={self.baro_altitude})"
        )
