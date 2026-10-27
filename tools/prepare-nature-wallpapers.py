#!/usr/bin/env python3
"""Prepare reviewed Unsplash photographs as TV images and independent thumbnails.

Network downloads are opt-in, HTTPS-only and bounded to 32 MiB. Source records
are reviewed manually against each original Unsplash page, never a search result.
The generated assets belong in the separate wallpaper repository, not the APK.
Requires Pillow; its ImageOps.fit crops without changing the source aspect ratio.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import urllib.parse
import urllib.request

from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageStat


def digest(path: Path) -> dict:
    return {"bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def download(url: str, path: Path) -> None:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != "images.unsplash.com":
        raise ValueError("Only reviewed HTTPS Unsplash image URLs may be downloaded")
    request = urllib.request.Request(url, headers={"User-Agent": "KarnarOs/0.3.2 WallpaperPreparation"})
    with urllib.request.urlopen(request, timeout=45) as response:
        if urllib.parse.urlparse(response.url).hostname != "images.unsplash.com":
            raise ValueError("Unexpected download redirect")
        data = response.read(32 * 1024 * 1024 + 1)
        if len(data) > 32 * 1024 * 1024:
            raise ValueError("Source image exceeds 32 MiB limit")
    with Image.open(io.BytesIO(data)) as probe:
        probe.verify()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--source-cache", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args()
    sources = json.loads(args.sources.read_text())
    records = []
    panels = []
    (args.output / "images").mkdir(parents=True, exist_ok=True)
    (args.output / "thumbnails").mkdir(parents=True, exist_ok=True)
    for entry in sources["photos"]:
        if entry.get("rightsVerified") is not True:
            raise ValueError(f"Unverified reuse rights: {entry['id']}")
        source = args.source_cache / (entry["id"] + ".jpg")
        if not source.exists():
            if not args.download:
                raise FileNotFoundError(f"{source}; use --download after reviewing rights")
            download(entry["downloadUrl"], source)
        with Image.open(source) as original:
            upright = ImageOps.exif_transpose(original).convert("RGB")
            if upright.width < 1920 or upright.height < 1080:
                raise ValueError(f"Insufficient source dimensions: {entry['id']} {upright.size}")
            image = ImageOps.fit(upright, (1920, 1080), method=Image.Resampling.LANCZOS,
                                 centering=tuple(entry.get("cropCenter", [0.5, 0.5])))
            output = args.output / "images" / (entry["id"] + ".jpg")
            image.save(output, "JPEG", quality=86, optimize=True, progressive=True, subsampling=2)
            thumb = args.output / "thumbnails" / (entry["id"] + ".jpg")
            image.resize((384, 216), Image.Resampling.LANCZOS).save(
                thumb, "JPEG", quality=78, optimize=True, progressive=True)
            record = {**entry, "sourcePixels": list(upright.size), "sourceDownload": digest(source),
                      "file": str(output.relative_to(args.output)), "width": 1920, "height": 1080,
                      **digest(output), "thumbnail": {"file": str(thumb.relative_to(args.output)),
                      "width": 384, "height": 216, **digest(thumb)}}
            gray = image.convert("L")
            record["interfaceMeanLuma"] = {
                "topLeft": round(ImageStat.Stat(gray.crop((100, 60, 500, 180))).mean[0], 2),
                "topCenter": round(ImageStat.Stat(gray.crop((700, 60, 1220, 180))).mean[0], 2),
                "topRight": round(ImageStat.Stat(gray.crop((1500, 60, 1820, 180))).mean[0], 2),
                "dock": round(ImageStat.Stat(gray.crop((96, 800, 1824, 1015))).mean[0], 2)}
            records.append(record)
            panel = Image.new("RGB", (512, 330), "#111820")
            panel.paste(image.resize((512, 288), Image.Resampling.LANCZOS), (0, 0))
            ImageDraw.Draw(panel).text((12, 298), entry["title"], fill="white", font=ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18))
            panels.append(panel)
            print(f"{entry['id']}: {output.stat().st_size} bytes, thumbnail {thumb.stat().st_size}")
    (args.output / "nature-manifest.json").write_text(json.dumps({
        "preparedFor": "KarnarOs 0.3.2", "sourceReviewDate": sources["reviewedOn"],
        "encoding": "JPEG 86 / 4:2:0 progressive; thumbnail JPEG 78 / 4:2:0 progressive",
        "crop": "ImageOps.fit Lanczos 16:9; no stretching; EXIF orientation applied",
        "wallpapers": records}, indent=2, ensure_ascii=False) + "\n")
    sheet = Image.new("RGB", (512 * 2, 330 * 5), "#111820")
    for index, panel in enumerate(panels):
        sheet.paste(panel, ((index % 2) * 512, (index // 2) * 330))
    sheet.save(args.output / "nature-contact-sheet.jpg", quality=90, optimize=True)


if __name__ == "__main__":
    main()
