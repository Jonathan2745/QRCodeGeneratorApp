from pathlib import Path

import pytest
from PIL import Image

from qrgenerator.qr_service import generate_qr_code, make_background_transparent


def test_generate_qr_code_creates_png_file(tmp_path: Path) -> None:
    output_path = tmp_path / "nested" / "qr-code.png"

    result = generate_qr_code("https://example.com", output_path)

    assert result == output_path
    assert output_path.exists()

    with Image.open(output_path) as image:
        assert image.format == "PNG"
        assert image.size[0] > 0
        assert image.size[1] > 0


@pytest.mark.parametrize("data", ["", "   ", "\n\t"])
def test_generate_qr_code_rejects_blank_input(tmp_path: Path, data: str) -> None:
    with pytest.raises(ValueError, match="QR code data cannot be empty"):
        generate_qr_code(data, tmp_path / "qr-code.png")


def test_make_background_transparent_converts_white_pixels_only() -> None:
    image = Image.new("RGBA", (2, 1))
    image.putdata(
        [
            (255, 255, 255, 255),
            (0, 0, 0, 255),
        ]
    )

    result = make_background_transparent(image)

    assert list(result.getdata()) == [
        (255, 255, 255, 0),
        (0, 0, 0, 255),
    ]
