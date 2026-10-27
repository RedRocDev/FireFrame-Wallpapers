#!/usr/bin/env python3
"""Generate or verify a FireFrame playlist from local files; never uses the network."""

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import sys
import tempfile
import unicodedata
from urllib.parse import quote


ROOT = Path(__file__).resolve().parent.parent
MAX_VIDEO_BYTES = 512 * 1024 * 1024
MAX_PLAYLIST_BYTES = 256 * 1024
ID = re.compile(r"[a-z0-9][a-z0-9_-]{0,63}\Z")
REPO = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")


def build(repository: str, revision: str) -> bytes:
    if not REPO.fullmatch(repository) or any(p in (".", "..") for p in repository.split("/")):
        raise ValueError("Repository must be OWNER/NAME")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", revision) or revision in (".", ".."):
        raise ValueError("Use a branch without slashes, tag or commit SHA for --ref")
    catalog = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
    entries = catalog.get("wallpapers") if isinstance(catalog, dict) else None
    if not isinstance(entries, list) or not 1 <= len(entries) <= 64:
        raise ValueError("catalog.json must contain 1–64 wallpapers")
    ids = set()
    result = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("Each wallpaper must be an object")
        identifier, title, filename = (entry.get(k) for k in ("id", "title", "file"))
        if not isinstance(identifier, str) or not ID.fullmatch(identifier) or identifier in ids:
            raise ValueError(f"Invalid or duplicate wallpaper ID: {identifier!r}")
        ids.add(identifier)
        if (not isinstance(title, str) or not title.strip() or len(title) > 80
                or any(unicodedata.category(c) == "Cc" for c in title)):
            raise ValueError(f"Invalid title for {identifier}")
        if not all(isinstance(entry.get(k), str) and entry[k].strip() for k in ("credit", "license")):
            raise ValueError(f"Credit and license are required for {identifier}")
        if not isinstance(filename, str) or "\\" in filename:
            raise ValueError(f"Invalid local filename for {identifier}")
        relative = PurePosixPath(filename)
        if relative.is_absolute() or ".." in relative.parts or relative.suffix.lower() != ".mp4":
            raise ValueError(f"Expected a relative MP4 path for {identifier}")
        video = (ROOT / filename).resolve()
        if not video.is_relative_to((ROOT / "videos").resolve()) or not video.is_file():
            raise ValueError(f"Video must be a file inside videos/: {filename}")
        length = video.stat().st_size
        if not 12 <= length <= MAX_VIDEO_BYTES:
            raise ValueError(f"Video must contain 12 bytes–512 MiB: {filename}")
        digest = hashlib.sha256()
        with video.open("rb") as source:
            header = source.read(12)
            if header[4:8] != b"ftyp":
                raise ValueError(f"Missing MP4 ftyp header: {filename}")
            digest.update(header)
            while chunk := source.read(65536):
                digest.update(chunk)
        result.append({
            "id": identifier,
            "title": title,
            "url": f"https://raw.githubusercontent.com/{repository}/{revision}/{quote(filename, safe='/')}",
            "sha256": digest.hexdigest(),
            "bytes": length,
        })
    payload = (json.dumps({"version": 1, "wallpapers": result}, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    if len(payload) > MAX_PLAYLIST_BYTES:
        raise ValueError("Generated playlist exceeds 256 KiB")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify committed playlist instead of writing")
    parser.add_argument("--repo", default="RedRocDev/FireFrame-Wallpapers", help="GitHub OWNER/NAME")
    parser.add_argument("--ref", default="main", help="Branch, tag or commit used in raw MP4 URLs")
    args = parser.parse_args()
    target = ROOT / "playlist.json"
    try:
        expected = build(args.repo, args.ref)
        if args.check:
            if not target.is_file() or target.read_bytes() != expected:
                raise ValueError("playlist.json is stale; run tools/playlist.py with matching --repo/--ref")
            print("Playlist verified: metadata, MP4 signature, sizes and SHA-256 match local videos")
        else:
            temporary = None
            try:
                with tempfile.NamedTemporaryFile(dir=ROOT, prefix="playlist-", suffix=".tmp", delete=False) as output:
                    temporary = Path(output.name)
                    output.write(expected)
                os.replace(temporary, target)
            finally:
                if temporary is not None:
                    temporary.unlink(missing_ok=True)
            print("Generated playlist.json from verified local videos")
        return 0
    except (OSError, ValueError, TypeError, KeyError) as error:
        print(f"Playlist error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
