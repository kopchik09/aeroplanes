import json

import requests

from src.api.adapters import OpenSkyNominatimAdapter
from src.service import AeroplaneService
from src.storage.json_storage import JSONAeroplaneStorage
from src.ui import user_interaction
from tests.helpers import sample_states

SPAIN = [{"boundingbox": ["41.0", "43.8", "-9.3", "3.3"]}]


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


class FakeInternet:
    """Заменяет requests.Session: отвечает как Nominatim и OpenSky, но без сети."""

    def __init__(self, nominatim=SPAIN, error=None):
        self.nominatim = nominatim
        self.error = error
        self.urls = []

    def get(self, url, params=None, headers=None, timeout=None):
        self.urls.append(url)
        if self.error:
            raise self.error
        if url == OpenSkyNominatimAdapter.NOMINATIM_URL:
            return FakeResponse(self.nominatim)
        return FakeResponse({"time": 1, "states": sample_states()})


def make_real_service(tmp_path, internet):
    return AeroplaneService(
        api=OpenSkyNominatimAdapter(session=internet),
        storage=JSONAeroplaneStorage(tmp_path / "planes.json"),
    )


def run_menu(monkeypatch, capsys, service, answers):
    """Проходит по меню с заранее заданными ответами и возвращает вывод программы."""
    answers_iter = iter(answers)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers_iter))
    user_interaction(service)
    return capsys.readouterr().out


def test_load_then_top_n(tmp_path, monkeypatch, capsys):
    service = make_real_service(tmp_path, FakeInternet())
    out = run_menu(monkeypatch, capsys, service, ["1", "Spain", "2", "2", "0"])
    assert "Загружено самолётов: 4" in out
    assert "IBE123" in out  # 11500 м
    assert "DLH1QM" in out  # 10668 м
    assert "SWR438A" not in out  # 4267 м, в топ-2 не попадает
    assert "Всего: 2" in out


def test_load_then_filter_by_registration(tmp_path, monkeypatch, capsys):
    service = make_real_service(tmp_path, FakeInternet())
    out = run_menu(monkeypatch, capsys, service, ["1", "Spain", "3", "Germany", "0"])
    assert "DLH1QM" in out
    assert "Всего: 1" in out


def test_loaded_planes_are_saved_to_json(tmp_path, monkeypatch, capsys):
    service = make_real_service(tmp_path, FakeInternet())
    run_menu(monkeypatch, capsys, service, ["1", "Spain", "0"])
    saved = json.loads((tmp_path / "planes.json").read_text(encoding="utf-8"))
    assert len(saved) == 4
    assert {row["origin_country"] for row in saved} == {
        "Switzerland",
        "Germany",
        "Spain",
    }


def test_repeated_load_does_not_duplicate(tmp_path, monkeypatch, capsys):
    service = make_real_service(tmp_path, FakeInternet())
    run_menu(monkeypatch, capsys, service, ["1", "Spain", "1", "Spain", "0"])
    assert len(service.storage.get_aeroplanes()) == 4


def test_data_survives_restart_without_network(tmp_path, monkeypatch, capsys):
    run_menu(
        monkeypatch,
        capsys,
        make_real_service(tmp_path, FakeInternet()),
        ["1", "Spain", "0"],
    )

    # Новый запуск программы: сети нет, а данные остаются в файле
    restarted = make_real_service(
        tmp_path, FakeInternet(error=requests.ConnectionError("нет сети"))
    )
    out = run_menu(monkeypatch, capsys, restarted, ["5", "0"])
    assert "IBE123" in out
    assert "Всего: 4" in out


def test_unknown_country_stops_before_opensky(tmp_path, monkeypatch, capsys):
    internet = FakeInternet(nominatim=[])
    service = make_real_service(tmp_path, internet)
    out = run_menu(monkeypatch, capsys, service, ["1", "Atlantis", "0"])
    assert "Страна «Atlantis» не найдена" in out
    assert internet.urls == [OpenSkyNominatimAdapter.NOMINATIM_URL]


def test_network_error_is_shown_and_program_continues(tmp_path, monkeypatch, capsys):
    service = make_real_service(
        tmp_path, FakeInternet(error=requests.ConnectionError("нет связи"))
    )
    out = run_menu(monkeypatch, capsys, service, ["1", "Spain", "0"])
    assert "Ошибка сети или API" in out
    assert "До встречи" in out
