#!/usr/bin/env python3
"""Build/verify the mixed-media catalog without modifying the legacy playlist."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://raw.githubusercontent.com/RedRocDev/FireFrame-Wallpapers/main/"


def media(relative, size=None):
    path = (ROOT / relative).resolve()
    if not path.is_relative_to(ROOT) or not path.is_file():
        raise ValueError(f"Missing or unsafe media path: {relative}")
    if size is not None:
        with Image.open(path) as image:
            if image.format != "JPEG" or image.size != size:
                raise ValueError(f"Unexpected JPEG dimensions: {relative}")
            image.verify()
    return {"url": BASE + relative, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "bytes": path.stat().st_size}


def build():
    legacy = json.loads((ROOT / "playlist.json").read_text())
    manifest = json.loads((ROOT / "nature-manifest.json").read_text())
    entries = []
    for video in legacy["wallpapers"]:
        relative = video["url"].removeprefix(BASE)
        if relative == video["url"] or media(relative) != {k: video[k] for k in ("url", "sha256", "bytes")}:
            raise ValueError("Legacy media must remain unchanged")
        entries.append({**video, "type": "video", "thumbnail": media(
            "thumbnails/" + video["id"] + ".jpg", (384, 216))})
    for image in manifest["wallpapers"]:
        if image.get("rightsVerified") is not True:
            raise ValueError(f"Unverified photo rights: {image['id']}")
        metadata = media(image["file"], (1920, 1080))
        if any(metadata[k] != image[k] for k in ("bytes", "sha256")):
            raise ValueError(f"Manifest checksum mismatch: {image['id']}")
        thumbnail = media(image["thumbnail"]["file"], (384, 216))
        if any(thumbnail[k] != image["thumbnail"][k] for k in ("bytes", "sha256")):
            raise ValueError(f"Thumbnail checksum mismatch: {image['id']}")
        entries.append({"id": image["id"], "title": image["title"], "type": "image", **metadata,
                        "thumbnail": thumbnail, "photographer": image["photographer"],
                        "sourcePage": image["sourcePage"], "licenseUrl": image["licenseUrl"]})
    if len({entry["id"] for entry in entries}) != len(entries):
        raise ValueError("Duplicate wallpaper ID")
    return (json.dumps({"version": 2, "wallpapers": entries}, indent=2, ensure_ascii=False) + "\n").encode()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        expected = build()
        path = ROOT / "playlist-v2.json"
        if args.check:
            if path.read_bytes() != expected:
                raise ValueError("playlist-v2.json is stale; regenerate it")
            print("Version 2 verified: legacy video unchanged, all images/thumbnails/dimensions/hashes match")
        else:
            path.write_bytes(expected)
            print("Generated playlist-v2.json; legacy playlist.json untouched")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Playlist error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
