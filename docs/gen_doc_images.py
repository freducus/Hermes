"""Generate PNG page images from example PDFs for Sphinx documentation."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMAGES_DIR = ROOT / "docs" / "source" / "_images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

EXAMPLES = [
    "basic_report",
    "engineering_report",
    "dashboard_report",
    "theme_demo",
    "nested_layouts",
    "padding_margin",
    "comprehensive_report",
    "image_demo",
    "figure_alignment",
]


def main() -> None:
    for name in EXAMPLES:
        pdf_path = ROOT / "examples" / f"{name}.pdf"
        if not pdf_path.exists():
            print(f"SKIP  {name}.pdf  (not found)")
            continue

        result = subprocess.run(
            [sys.executable, "-m", "pypdfium2_cli", "render", str(pdf_path),
             "--output", str(IMAGES_DIR), "--scale", "2"],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            print(f"ERROR {name}: {result.stderr.strip()}")
        else:
            print(f"OK    {name}")

    files = sorted(IMAGES_DIR.glob("*.png"))
    print(f"\n{len(files)} images in {IMAGES_DIR}")


if __name__ == "__main__":
    main()
