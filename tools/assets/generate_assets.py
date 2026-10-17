"""One-shot asset forge: run once, commit the PNGs, never regenerate at game time.

Usage (from the repo root):  python3 tools/assets/generate_assets.py
"""
from __future__ import annotations

import json
from pathlib import Path

import font
import fighters
import palette
import stage
import ui

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "assets"


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def generate_fighters() -> None:
    target = ensure_dir(ASSETS / "fighters")
    ui_target = ensure_dir(ASSETS / "ui")
    for fighter_id, artist in fighters.build_artists().items():
        artist.render_sheet().save(target / f"{fighter_id}.png")
        ui.render_portrait(artist).save(ui_target / f"portrait_{fighter_id}.png")
        ui.render_stock_icon(artist).save(ui_target / f"stock_{fighter_id}.png")
    (target / "layout.json").write_text(json.dumps(fighters.build_layout(), indent=2))


def generate_stage() -> None:
    target = ensure_dir(ASSETS / "stage")
    stage.render_sky().save(target / "sky.png")
    stage.render_clouds().save(target / "clouds.png")
    stage.render_far().save(target / "far.png")
    stage.render_mid().save(target / "mid.png")
    stage.render_island().save(target / "island.png")
    stage.render_platform().save(target / "platform.png")
    fx = ensure_dir(ASSETS / "fx")
    stage.render_hit_spark().save(fx / "hit_spark.png")
    stage.render_eco_bolt(palette.ECO_YELLOW).save(fx / "eco_bolt.png")


def generate_ui() -> None:
    target = ensure_dir(ASSETS / "ui")
    ui.render_logo().save(target / "logo.png")
    for name, panel in ui.render_panels().items():
        panel.save(str(target / f"{name}.png"))
    ui.render_selector((236, 70, 70), "1P").save(target / "selector_p1.png")
    ui.render_selector((70, 140, 240), "2P").save(target / "selector_p2.png")
    ui.render_selector((150, 150, 160), "BOT").save(target / "selector_bot.png")
    fonts = ensure_dir(ASSETS / "fonts")
    atlas, descriptor = font.render_font("eco_pixel.png")
    atlas.save(fonts / "eco_pixel.png")
    (fonts / "eco_pixel.fnt").write_text(descriptor, encoding="utf-8")
    ui.render_portrait(fighters.build_artists()["kael"]).resize((128, 128)).save(ROOT / "icon.png")


if __name__ == "__main__":
    generate_fighters()
    generate_stage()
    generate_ui()
    print(f"Assets written to {ASSETS}")
