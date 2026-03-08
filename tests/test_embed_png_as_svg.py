"""
Unit tests for src/scripts/embed_png_as_svg.py
"""

import sys
from pathlib import Path

from PIL import Image


sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "scripts"))

import embed_png_as_svg as eps


class TestEmbedPngAsSvg:
    def test_wrap_png_as_svg_preserves_dimensions_and_embeds_data(self, tmp_path):
        input_png = tmp_path / "logo.png"
        output_svg = tmp_path / "logo.svg"

        Image.new("RGBA", (12, 18), (255, 0, 0, 255)).save(input_png)

        eps.wrap_png_as_svg(input_png, output_svg)

        text = output_svg.read_text(encoding="utf-8")
        assert 'width="12"' in text
        assert 'height="18"' in text
        assert 'data:image/png;base64,' in text
