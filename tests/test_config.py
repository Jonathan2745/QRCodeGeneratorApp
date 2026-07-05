import sys
from pathlib import Path

import qrgenerator.config as config


def test_get_app_root_uses_source_root_when_not_frozen(monkeypatch) -> None:
    monkeypatch.delattr(sys, "frozen", raising=False)

    assert config._get_app_root() == Path(config.__file__).resolve().parents[2]


def test_get_app_root_uses_executable_directory_when_frozen(monkeypatch, tmp_path: Path) -> None:
    executable_path = tmp_path / "QRGenerator.exe"
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", str(executable_path))

    assert config._get_app_root() == tmp_path
