import pytest

from src.api.adapters import CountryNotFoundError
from src.ui import user_interaction
from tests.helpers import make_service, sample_states


def script_input(monkeypatch, answers):
    """Подменяет input(): программа получает ответы из списка по порядку."""
    answers_iter = iter(answers)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers_iter))


@pytest.fixture
def loaded_service(tmp_path):
    service = make_service(tmp_path, sample_states())
    service.load_country("Spain")
    return service


def test_exit_prints_goodbye(tmp_path, monkeypatch, capsys):
    service = make_service(tmp_path)
    script_input(monkeypatch, ["0"])
    user_interaction(service)
    assert "До встречи" in capsys.readouterr().out


def test_unknown_menu_item_is_reported(tmp_path, monkeypatch, capsys):
    service = make_service(tmp_path)
    script_input(monkeypatch, ["9", "0"])
    user_interaction(service)
    assert "Такого пункта нет" in capsys.readouterr().out


def test_load_country_saves_planes(tmp_path, monkeypatch, capsys):
    service = make_service(tmp_path, sample_states())
    script_input(monkeypatch, ["1", "Spain", "0"])
    user_interaction(service)
    assert "Загружено самолётов: 4" in capsys.readouterr().out
    assert len(service.storage.get_aeroplanes()) == 4


def test_empty_country_name_is_rejected(tmp_path, monkeypatch, capsys):
    service = make_service(tmp_path, sample_states())
    script_input(monkeypatch, ["1", "   ", "0"])
    user_interaction(service)
    assert "не может быть пустым" in capsys.readouterr().out
    assert service.api.requested_countries == []


def test_unknown_country_shows_error(tmp_path, monkeypatch, capsys):
    service = make_service(tmp_path)

    def not_found(country):
        raise CountryNotFoundError(f"Страна «{country}» не найдена")

    monkeypatch.setattr(service.api, "get_country_bbox", not_found)
    script_input(monkeypatch, ["1", "Atlantis", "0"])
    user_interaction(service)
    assert "Atlantis" in capsys.readouterr().out


def test_top_n_asks_again_on_bad_input(loaded_service, monkeypatch, capsys):
    script_input(monkeypatch, ["2", "abc", "0", "2", "0"])
    user_interaction(loaded_service)
    out = capsys.readouterr().out
    assert "Нужно ввести целое число" in out
    assert "Число должно быть больше нуля" in out
    assert "Всего: 2" in out


def test_registration_filter(loaded_service, monkeypatch, capsys):
    script_input(monkeypatch, ["3", "Switzerland, Germany", "0"])
    user_interaction(loaded_service)
    out = capsys.readouterr().out
    assert "SWR438A" in out
    assert "DLH1QM" in out
    assert "IBE123" not in out


def test_altitude_range_with_swapped_bounds_is_reported(
    loaded_service, monkeypatch, capsys
):
    script_input(monkeypatch, ["4", "10000", "5000", "0"])
    user_interaction(loaded_service)
    assert "Минимальная высота больше максимальной" in capsys.readouterr().out


def test_remove_on_ground(loaded_service, monkeypatch, capsys):
    script_input(monkeypatch, ["6", "0"])
    user_interaction(loaded_service)
    assert "Удалено самолётов на земле: 1" in capsys.readouterr().out
