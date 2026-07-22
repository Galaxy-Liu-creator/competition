"""Create non-destructive 4x presentation copies of the Stitch UI screenshots."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter


WORKSPACE = Path(__file__).resolve().parents[1]
SOURCE_DIR = WORKSPACE / "picture" / "Stitch生成稿"
OUTPUT_DIR = WORKSPACE / "picture" / "Stitch生成稿-高清"
SCALE = 4


def upscale_ui(source_path: Path, output_path: Path) -> None:
    with Image.open(source_path) as source:
        image = source.convert("RGB")
        target_size = (image.width * SCALE, image.height * SCALE)

        # Lanczos preserves UI geometry better than generative upscaling and does
        # not invent or alter Chinese copy, device IDs, charts, or table values.
        enhanced = image.resize(target_size, Image.Resampling.LANCZOS)
        enhanced = enhanced.filter(
            ImageFilter.UnsharpMask(radius=1.15, percent=115, threshold=3)
        )
        enhanced = ImageEnhance.Contrast(enhanced).enhance(1.02)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        enhanced.save(output_path, format="PNG", optimize=True)


def main() -> None:
    if not SOURCE_DIR.exists():
        raise SystemExit(f"Source directory does not exist: {SOURCE_DIR}")

    source_files = sorted(SOURCE_DIR.glob("*.png"))
    if not source_files:
        raise SystemExit(f"No PNG images found in: {SOURCE_DIR}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    expected_outputs: set[Path] = set()

    for source_path in source_files:
        output_path = OUTPUT_DIR / source_path.name
        expected_outputs.add(output_path.resolve())
        upscale_ui(source_path, output_path)
        print(f"{source_path.name}: 512x410 -> 2048x1640")

    # Remove only stale PNGs in the generated output directory. Source assets
    # and non-PNG user files are never touched.
    for output_path in OUTPUT_DIR.glob("*.png"):
        if output_path.resolve() not in expected_outputs:
            output_path.unlink()

    print(f"Generated {len(source_files)} enhanced images in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
