import math

import requests

from src.api.adapters import CountryNotFoundError
from src.models.aeroplane import Aeroplane
from src.service import AeroplaneService

MENU = """
========== Самолёты над странами ==========
1 — загрузить самолёты над страной (из OpenSky)
2 — топ-N самолётов по высоте
3 — самолёты по стране регистрации
4 — самолёты в диапазоне высот
5 — показать все сохранённые самолёты
6 — удалить самолёты, которые стоят на земле
0 — выход
============================================"""


def print_aeroplanes(planes: list[Aeroplane]) -> None:
    if not planes:
        print("Самолёты не найдены.")
        return
    print(
        f"{'#':>4}  {'Позывной':<10} {'Страна регистрации':<22} {'Высота, м':>10} {'Скорость, м/с':>14}"
    )
    for number, plane in enumerate(planes, start=1):
        print(
            f"{number:>4}  {plane.callsign:<10} {plane.origin_country:<22} "
            f"{plane.baro_altitude:>10.0f} {plane.velocity:>14.1f}"
        )
    print(f"Всего: {len(planes)}")


def ask_positive_int(prompt: str) -> int:
    while True:
        try:
            value = int(input(prompt).strip())
        except ValueError:
            print("Нужно ввести целое число.")
            continue
        if value > 0:
            return value
        print("Число должно быть больше нуля.")


def ask_number(prompt: str) -> float:
    while True:
        try:
            value = float(input(prompt).strip().replace(",", "."))
        except ValueError:
            print("Нужно ввести число.")
            continue
        if math.isfinite(value):
            return value
        print("Число должно быть конечным.")


def _load_country(service: AeroplaneService) -> None:
    country = input("Введите название страны на английском (например, Spain): ").strip()
    if not country:
        print("Название страны не может быть пустым.")
        return
    count = service.load_country(country)
    print(f"Загружено самолётов: {count}")


def _top_by_altitude(service: AeroplaneService) -> None:
    n = ask_positive_int("Сколько самолётов вывести? ")
    print_aeroplanes(service.top_by_altitude(n))


def _by_registration(service: AeroplaneService) -> None:
    raw = input("Страны регистрации через запятую (например, Spain, France): ")
    countries = [name for name in raw.split(",") if name.strip()]
    if not countries:
        print("Нужно ввести хотя бы одну страну.")
        return
    print_aeroplanes(service.by_registration(countries))


def _by_altitude_range(service: AeroplaneService) -> None:
    low = ask_number("Минимальная высота, м: ")
    high = ask_number("Максимальная высота, м: ")
    print_aeroplanes(service.by_altitude_range(low, high))


def _show_all(service: AeroplaneService) -> None:
    print_aeroplanes(service.get_all())


def _remove_on_ground(service: AeroplaneService) -> None:
    print(f"Удалено самолётов на земле: {service.remove_on_ground()}")


# Таблица «пункт меню → функция». Чтобы добавить пункт, достаточно дописать строку.
ACTIONS = {
    "1": _load_country,
    "2": _top_by_altitude,
    "3": _by_registration,
    "4": _by_altitude_range,
    "5": _show_all,
    "6": _remove_on_ground,
}


def user_interaction(service: AeroplaneService) -> None:
    """Главный цикл программы: показывает меню и выполняет выбранный пункт."""
    while True:
        print(MENU)
        choice = input("Выберите пункт: ").strip()

        if choice == "0":
            print("До встречи!")
            return

        action = ACTIONS.get(choice)
        if action is None:
            print("Такого пункта нет, попробуйте ещё раз.")
            continue

        try:
            action(service)
        except CountryNotFoundError as error:
            print(error)
        except requests.RequestException as error:
            print(f"Ошибка сети или API: {error}")
        except ValueError as error:
            print(f"Некорректные данные: {error}")
