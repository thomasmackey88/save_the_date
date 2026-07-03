from __future__ import annotations

import re
import shutil
import textwrap
import webbrowser
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INDEX_PATH = BASE_DIR / "index.html"
STYLE_PATH = BASE_DIR / "style.css"
OUTPUT_DIR = BASE_DIR / "font_variants"

# Each option controls: Google Fonts URL, heading font stack, and body font stack.
FONT_VARIANTS = [
    {
        "id": "greatvibes-manrope",
        "name": "Great Vibes + Manrope",
        "href": "https://fonts.googleapis.com/css2?family=Great+Vibes&family=Manrope:wght@400;500;700&display=swap",
        "heading": "'Great Vibes', cursive",
        "body": "'Manrope', sans-serif",
    },
    {
        "id": "dancingscript-nunito",
        "name": "Dancing Script + Nunito Sans",
        "href": "https://fonts.googleapis.com/css2?family=Dancing+Script:wght@500;700&family=Nunito+Sans:wght@400;600;700&display=swap",
        "heading": "'Dancing Script', cursive",
        "body": "'Nunito Sans', sans-serif",
    },
    {
        "id": "allura-lato",
        "name": "Allura + Lato",
        "href": "https://fonts.googleapis.com/css2?family=Allura&family=Lato:wght@400;700&display=swap",
        "heading": "'Allura', cursive",
        "body": "'Lato', sans-serif",
    },
    {
        "id": "parisienne-opensans",
        "name": "Parisienne + Open Sans",
        "href": "https://fonts.googleapis.com/css2?family=Parisienne&family=Open+Sans:wght@400;600;700&display=swap",
        "heading": "'Parisienne', cursive",
        "body": "'Open Sans', sans-serif",
    },
    {
        "id": "playfair-source",
        "name": "Playfair Display + Source Sans 3",
        "href": "https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Source+Sans+3:wght@400;600;700&display=swap",
        "heading": "'Playfair Display', serif",
        "body": "'Source Sans 3', sans-serif",
    },
    {
        "id": "lora-nunito",
        "name": "Lora + Nunito Sans",
        "href": "https://fonts.googleapis.com/css2?family=Lora:wght@500;700&family=Nunito+Sans:wght@400;600;700&display=swap",
        "heading": "'Lora', serif",
        "body": "'Nunito Sans', sans-serif",
    },
    {
        "id": "cinzel-opensans",
        "name": "Cinzel + Open Sans",
        "href": "https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700&family=Open+Sans:wght@400;600;700&display=swap",
        "heading": "'Cinzel', serif",
        "body": "'Open Sans', sans-serif",
    },
    {
        "id": "dmserif-lato",
        "name": "DM Serif Display + Lato",
        "href": "https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Lato:wght@400;700&display=swap",
        "heading": "'DM Serif Display', serif",
        "body": "'Lato', sans-serif",
    },
    {
        "id": "ebgaramond-montserrat",
        "name": "EB Garamond + Montserrat",
        "href": "https://fonts.googleapis.com/css2?family=EB+Garamond:wght@500;700&family=Montserrat:wght@400;600;700&display=swap",
        "heading": "'EB Garamond', serif",
        "body": "'Montserrat', sans-serif",
    },
    {
        "id": "libre-franklin",
        "name": "Libre Baskerville + Libre Franklin",
        "href": "https://fonts.googleapis.com/css2?family=Libre+Baskerville:wght@700&family=Libre+Franklin:wght@400;600;700&display=swap",
        "heading": "'Libre Baskerville', serif",
        "body": "'Libre Franklin', sans-serif",
    },
]


def update_html_font_link(html_text: str, new_href: str) -> str:
    google_link_pattern = re.compile(
        r'<link\s+href="https://fonts\.googleapis\.com/css2[^\"]*"\s+rel="stylesheet">'
    )

    replacement = f'<link href="{new_href}" rel="stylesheet">'
    updated_html, count = google_link_pattern.subn(replacement, html_text, count=1)

    if count > 0:
        return updated_html

    marker = '<link rel="stylesheet" href="style.css">'
    if marker in html_text:
        return html_text.replace(marker, replacement + "\n    " + marker, 1)

    return html_text


def update_css_fonts(css_text: str, heading_stack: str, body_stack: str) -> str:
    updated_css = css_text

    body_pattern = re.compile(r"(body\s*\{[^}]*?font-family:\s*)[^;]+;", re.DOTALL)
    updated_css, body_count = body_pattern.subn(rf"\1{body_stack};", updated_css, count=1)

    heading_pattern = re.compile(r"(h1\s*,\s*\nh2\s*,\s*\nh3\s*\{[^}]*?font-family:\s*)[^;]+;", re.DOTALL)
    updated_css, heading_count = heading_pattern.subn(rf"\1{heading_stack};", updated_css, count=1)

    if body_count == 0:
        updated_css += f"\n\nbody {{\n    font-family: {body_stack};\n}}\n"

    if heading_count == 0:
        updated_css += textwrap.dedent(
            f"""

            h1,
            h2,
            h3 {{
                font-family: {heading_stack};
            }}
            """
        )

    return updated_css


def generate_variant_files(base_html: str, base_css: str) -> list[dict[str, str]]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    variants_info: list[dict[str, str]] = []

    for variant in FONT_VARIANTS:
        variant_dir = OUTPUT_DIR / variant["id"]
        variant_dir.mkdir(parents=True, exist_ok=True)

        variant_html = update_html_font_link(base_html, variant["href"])
        variant_css = update_css_fonts(base_css, variant["heading"], variant["body"])

        (variant_dir / "index.html").write_text(variant_html, encoding="utf-8")
        (variant_dir / "style.css").write_text(variant_css, encoding="utf-8")

        variants_info.append(
            {
                "id": variant["id"],
                "name": variant["name"],
                "path": str((variant_dir / "index.html").resolve()),
            }
        )

    return variants_info


def build_gallery_html(variants_info: list[dict[str, str]]) -> str:
    cards = []
    for idx, variant in enumerate(variants_info, start=1):
        cards.append(
            f"""
            <article class=\"card\">
              <h2>{idx}. {variant['name']}</h2>
              <p>Variant key: <code>{variant['id']}</code></p>
              <iframe src=\"{variant['id']}/index.html\" title=\"{variant['name']} preview\"></iframe>
            </article>
            """
        )

    return f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>Wedding Font Picker</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: 'Segoe UI', Arial, sans-serif;
      background: #f2f6fa;
      color: #1f2937;
      padding: 24px;
    }}
    h1 {{ margin-top: 0; }}
    .help {{
      background: #eaf2ff;
      border: 1px solid #bfd8ff;
      border-radius: 10px;
      padding: 12px 14px;
      margin-bottom: 20px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
      gap: 16px;
    }}
    .card {{
      background: #ffffff;
      border: 1px solid #dbe5ef;
      border-radius: 12px;
      padding: 12px;
      box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
    }}
    .card h2 {{ margin: 0 0 8px 0; font-size: 1.05rem; }}
    .card p {{ margin: 0 0 10px 0; }}
    iframe {{
      width: 100%;
      height: 640px;
      border: 1px solid #d7e0e9;
      border-radius: 8px;
      background: #fff;
    }}
    code {{
      background: #f4f8fc;
      border: 1px solid #dbe5ef;
      border-radius: 6px;
      padding: 2px 6px;
    }}
  </style>
</head>
<body>
  <h1>Wedding Font Picker</h1>
  <p class=\"help\">Preview each option, then return to the terminal and type the number you want to apply to your real <code>index.html</code> and <code>style.css</code> files.</p>
  <section class=\"grid\">
    {''.join(cards)}
  </section>
</body>
</html>
"""


def backup_original_files() -> None:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = BASE_DIR / "font_variants" / "backups" / stamp
    backup_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(INDEX_PATH, backup_dir / "index.html")
    shutil.copy2(STYLE_PATH, backup_dir / "style.css")


def apply_variant(variant_id: str, base_html: str, base_css: str) -> None:
    selected = next((v for v in FONT_VARIANTS if v["id"] == variant_id), None)
    if not selected:
        raise ValueError(f"Unknown variant id: {variant_id}")

    backup_original_files()

    updated_html = update_html_font_link(base_html, selected["href"])
    updated_css = update_css_fonts(base_css, selected["heading"], selected["body"])

    INDEX_PATH.write_text(updated_html, encoding="utf-8")
    STYLE_PATH.write_text(updated_css, encoding="utf-8")


def run_interactive_picker(variants_info: list[dict[str, str]], base_html: str, base_css: str) -> None:
    print("\nFont options:")
    for idx, variant in enumerate(FONT_VARIANTS, start=1):
        print(f"  {idx}. {variant['name']} ({variant['id']})")

    choice = input("\nType a number to apply that font pair, or press Enter to keep current files: ").strip()
    if not choice:
        print("No changes applied to live files.")
        return

    if not choice.isdigit():
        print("Invalid input. Please run again and enter a number.")
        return

    index = int(choice)
    if index < 1 or index > len(FONT_VARIANTS):
        print("Number out of range. Please run again.")
        return

    selected_variant = FONT_VARIANTS[index - 1]
    apply_variant(selected_variant["id"], base_html, base_css)
    print(f"Applied: {selected_variant['name']}")
    print("Backup created under font_variants/backups/")


def main() -> None:
    if not INDEX_PATH.exists() or not STYLE_PATH.exists():
        raise FileNotFoundError("index.html and style.css must exist in the same folder as this script.")

    base_html = INDEX_PATH.read_text(encoding="utf-8")
    base_css = STYLE_PATH.read_text(encoding="utf-8")

    variants_info = generate_variant_files(base_html, base_css)

    gallery_html = build_gallery_html(variants_info)
    gallery_path = OUTPUT_DIR / "gallery.html"
    gallery_path.write_text(gallery_html, encoding="utf-8")

    print(f"Generated {len(variants_info)} preview variants in: {OUTPUT_DIR}")
    print(f"Opening gallery: {gallery_path}")
    webbrowser.open(gallery_path.resolve().as_uri())

    run_interactive_picker(variants_info, base_html, base_css)


if __name__ == "__main__":
    main()
