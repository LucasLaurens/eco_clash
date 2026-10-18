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
# Slot tags match MatchConfig.resolve_slot_tag on the Godot side.
SLOTS = (("p1", palette.SLOT_P1, "1P"), ("p2", palette.SLOT_P2, "2P"), ("bot", palette.SLOT_BOT, "BOT"))


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
    stage.render_pylon_glow().save(target / "pylon_glow.png")
    stage.render_flux_motes().save(target / "flux_motes.png")
    (target / "animated_layers.json").write_text(json.dumps(stage.build_animated_layers(), indent=2))
    fx_target = ensure_dir(ASSETS / "fx")
    stage.render_hit_spark().save(fx_target / "hit_spark.png")
    stage.render_flux_bolt(palette.FLUX_YELLOW).save(fx_target / "flux_bolt.png")
    stage.render_flux_bolt(palette.FLUX_DARK).save(fx_target / "flux_bolt_dark.png")
    stage.render_shadow().save(fx_target / "shadow.png")
    stage.render_dust().save(fx_target / "dust.png")
    stage.render_ko_burst().save(fx_target / "ko_burst.png")


def generate_ui() -> None:
    target = ensure_dir(ASSETS / "ui")
    ui.render_logo().save(target / "logo.png")
    for name, panel in ui.render_panels().items():
        panel.save(str(target / f"{name}.png"))
    for slot_tag, color, label in SLOTS:
        ui.render_selector(color, label).save(target / f"selector_{slot_tag}.png")
        ui.render_slot_marker(color, label).save(target / f"marker_{slot_tag}.png")
    fonts_target = ensure_dir(ASSETS / "fonts")
    atlas, descriptor = font.render_font("eco_pixel.png")
    atlas.save(fonts_target / "eco_pixel.png")
    (fonts_target / "eco_pixel.fnt").write_text(descriptor, encoding="utf-8")
    ui.render_portrait(fighters.build_artists()["kael"]).resize((128, 128)).save(ROOT / "icon.png")


if __name__ == "__main__":
    generate_fighters()
    generate_stage()
    generate_ui()
    print(f"Assets written to {ASSETS}")
