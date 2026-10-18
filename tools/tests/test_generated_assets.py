"""Feature: the committed assets are exactly what the generator produces today.

Fails when the drawing code changed but nobody regenerated, or a PNG was edited by hand.
Pixels are compared, not bytes, so a different Pillow version encoding the same image still passes.
"""

from pathlib import Path

from PIL import Image

import generate_assets

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "assets"
TEXT_EXTENSIONS = {".json", ".fnt"}
IMAGE_EXTENSION = ".png"


def test_committed_assets_match_the_generator(tmp_path: Path) -> None:
    # Arrange
    generated_root = tmp_path / "assets"
    icon_path = tmp_path / "icon.png"
    # Act
    generate_assets.generate_all(generated_root, icon_path)
    # Assert
    generated = sorted(path.relative_to(generated_root) for path in generated_root.rglob("*") if path.is_file())
    assert generated, "generator wrote nothing"
    mismatches = [
        str(relative) for relative in generated if not _is_same_file(generated_root / relative, ASSETS / relative)
    ]
    assert _is_same_file(icon_path, ROOT / "icon.png"), "regenerate icon.png"
    assert mismatches == [], f"regenerate assets: {mismatches}"


def _is_same_file(generated: Path, committed: Path) -> bool:
    if not committed.exists():
        return False
    if generated.suffix in TEXT_EXTENSIONS:
        return generated.read_text(encoding="utf-8") == committed.read_text(encoding="utf-8")
    if generated.suffix == IMAGE_EXTENSION:
        with Image.open(generated) as fresh, Image.open(committed) as stored:
            return fresh.size == stored.size and fresh.convert("RGBA").tobytes() == stored.convert("RGBA").tobytes()
    return generated.read_bytes() == committed.read_bytes()
