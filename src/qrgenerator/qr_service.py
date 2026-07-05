from __future__ import annotations

from pathlib import Path

import qrcode
from PIL import Image

from qrgenerator.config import (
    QR_BACK_COLOR,
    QR_BORDER,
    QR_BOX_SIZE,
    QR_FILL_COLOR,
    QR_TRANSPARENT_BACKGROUND,
)


def make_background_transparent(image: Image.Image) -> Image.Image:
    """
    Convert white pixels to transparent pixels.
    """
    rgba_image = image.convert("RGBA")

    pixels = rgba_image.getdata()
    new_pixels = []

    for r, g, b, _a in pixels:
        if (r, g, b) == (255, 255, 255):
            new_pixels.append((255, 255, 255, 0))
        else:
            new_pixels.append((0, 0, 0, 255))

    rgba_image.putdata(new_pixels)
    return rgba_image


def generate_qr_code(data: str, output_path: Path) -> Path:
    """
    Generate a QR code image and save it to output_path.
    """
    if not data.strip():
        raise ValueError("QR code data cannot be empty.")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=QR_BOX_SIZE,
        border=QR_BORDER,
    )

    qr.add_data(data)
    qr.make(fit=True)

    image = qr.make_image(
        fill_color=QR_FILL_COLOR,
        back_color=QR_BACK_COLOR,
    ).convert("RGBA")

    if QR_TRANSPARENT_BACKGROUND:
        image = make_background_transparent(image)

    image.save(output_path)

    return output_path
