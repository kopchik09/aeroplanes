from main import build_service
from src.api.adapters import OpenSkyNominatimAdapter
from src.storage.json_storage import JSONAeroplaneStorage


def test_build_service_wires_real_components(tmp_path):
    service = build_service(tmp_path / "planes.json")
    assert isinstance(service.api, OpenSkyNominatimAdapter)
    assert isinstance(service.storage, JSONAeroplaneStorage)
    assert service.storage.path == tmp_path / "planes.json"
