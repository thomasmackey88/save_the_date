#!/usr/bin/env python3
"""Generate multiple Wedding Flappy HTML variants for a given picture radius.

Usage:
  python generate_flappy_variants.py 30
  python generate_flappy_variants.py 30 --template wedding_flappy.html --outdir flappy_variants
"""

from __future__ import annotations

import math
import re
from pathlib import Path


BASELINE = {
    "radius": 44.0,
    "gravity": 0.45,
    "flap": -7.8,
    "speed": 2.6,
    "spawn_every": 1500.0,
    "pipe_width": 84.0,
    "floor_height": 86.0,
}


PROFILES = [
    {
        "name": "challenge",
        "e_target": 145.0,
        "gravity_mul": 1.05,
        "speed_mul": 1.06,
        "flap_mul": 1.00,
        "spawn_mul": 0.95,
    },
    {
        "name": "balanced",
        "e_target": 160.0,
        "gravity_mul": 1.00,
        "speed_mul": 1.00,
        "flap_mul": 1.00,
        "spawn_mul": 1.00,
    },
    {
        "name": "relaxed",
        "e_target": 175.0,
        "gravity_mul": 0.95,
        "speed_mul": 0.94,
        "flap_mul": 1.00,
        "spawn_mul": 1.06,
    },
    {
        "name": "easy",
        "e_target": 190.0,
        "gravity_mul": 0.90,
        "speed_mul": 0.90,
        "flap_mul": 0.98,
        "spawn_mul": 1.12,
    },
]


def format_num(value: float, digits: int = 4) -> str:
    text = f"{value:.{digits}f}".rstrip("0").rstrip(".")
    return text if text else "0"


def replace_property(source: str, prop: str, value: float) -> str:
    pattern = rf"(\b{re.escape(prop)}\s*:\s*)(-?\d+(?:\.\d+)?)"
    replaced, count = re.subn(pattern, rf"\g<1>{format_num(value)}", source, count=1)
    if count != 1:
        raise ValueError(f"Could not replace property '{prop}'.")
    return replaced


def replace_literal(source: str, old: str, new: str) -> str:
    if old not in source:
        raise ValueError(f"Expected text not found: {old}")
    return source.replace(old, new, 1)


def compute_settings(radius: float, profile: dict[str, float]) -> dict[str, float]:
    q = radius / BASELINE["radius"]

    auto_gravity = BASELINE["gravity"] * (1 - 0.20 * (q - 1))
    auto_speed = BASELINE["speed"] * (1 - 0.30 * (q - 1))
    auto_spawn = BASELINE["spawn_every"] * (1 + 0.25 * (q - 1))
    auto_flap = -abs(BASELINE["flap"]) * math.sqrt(auto_gravity / BASELINE["gravity"])

    gravity = auto_gravity * profile["gravity_mul"]
    speed = auto_speed * profile["speed_mul"]
    flap = auto_flap * profile["flap_mul"]
    spawn_every = auto_spawn * profile["spawn_mul"]
    pipe_gap = 2 * radius + profile["e_target"]

    return {
        "radius": radius,
        "gravity": gravity,
        "flap": flap,
        "speed": speed,
        "pipeGap": pipe_gap,
        "pipeWidth": BASELINE["pipe_width"],
        "spawnEvery": spawn_every,
        "floorHeight": BASELINE["floor_height"],
    }


def render_variant(template: str, profile_name: str, settings: dict[str, float]) -> str:
    out = template

    # Label the tab title so you can quickly tell which variant is open.
    out = replace_literal(out, "<title>Wedding Flappy</title>", f"<title>Wedding Flappy - {profile_name}</title>")

    # Update world constants.
    out = replace_property(out, "gravity", settings["gravity"])
    out = replace_property(out, "flap", settings["flap"])
    out = replace_property(out, "speed", settings["speed"])
    out = replace_property(out, "pipeGap", settings["pipeGap"])
    out = replace_property(out, "pipeWidth", settings["pipeWidth"])
    out = replace_property(out, "spawnEvery", settings["spawnEvery"])
    out = replace_property(out, "floorHeight", settings["floorHeight"])

    # Update picture radius.
    out = replace_property(out, "r", settings["radius"])

    return out


def main() -> None:
    radius = 50.0
    project_dir = Path(__file__).resolve().parent
    template_path = project_dir / "wedding_flappy.html"
    outdir = project_dir / "flappy_variants" / f"r{format_num(radius)}"

    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")

    outdir.mkdir(parents=True, exist_ok=True)

    template = template_path.read_text(encoding="utf-8")

    created = []
    for profile in PROFILES:
        settings = compute_settings(radius, profile)
        html = render_variant(template, profile["name"], settings)
        filename = f"wedding_flappy_r{format_num(radius)}_{profile['name']}.html"
        out_path = outdir / filename
        out_path.write_text(html, encoding="utf-8")
        created.append((out_path, settings))

    print("Created variants:")
    for path, settings in created:
        print(
            f"- {path} | gap={format_num(settings['pipeGap'])}, "
            f"speed={format_num(settings['speed'])}, gravity={format_num(settings['gravity'])}, "
            f"flap={format_num(settings['flap'])}, spawnEvery={format_num(settings['spawnEvery'])}"
        )


if __name__ == "__main__":
    main()
