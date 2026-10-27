# Nature wallpaper credits and reuse rights

Reviewed against the ten exact original Unsplash photo pages on **2026-10-27**. Every page identifies the photographer and explicitly links free reuse under the [Unsplash License](https://unsplash.com/license). None is an Unsplash+ image. No source was substituted.

These photographs remain subject to the Unsplash License, **not this repository’s MIT software licence**. The licence allows downloading, copying, modifying, distributing and using the images, including commercially. It excludes sale without significant modification and compiling a competing image service. This is a small curated wallpaper pack for the KarnarOs launcher. Photographer credits and original source links are retained below and in `playlist-v2.json`.

## Exact sources

| Wallpaper | Photographer and original source | Photo ID |
| --- | --- | --- |
| Mountain Lake | [Jonny Gios](https://unsplash.com/photos/mountain-landscape-reflected-in-a-calm-lake-IWhpMyaol8c) | `IWhpMyaol8c` |
| Misty Forest | [Jonny Gios](https://unsplash.com/photos/misty-forest-landscape-with-silhouetted-trees-mvby_QPxVxg) | `mvby_QPxVxg` |
| Iceland Waterfall | [Arthur Ogleznev](https://unsplash.com/photos/a-waterfall-with-a-river-running-under-it-c_iGQ5U2r6w) | `c_iGQ5U2r6w` |
| Tropical Beach | [Colin Watts](https://unsplash.com/photos/a-tropical-beach-with-palm-trees-and-clear-water-slj5hTTA8uM) | `slj5hTTA8uM` |
| Northern Lights | [Rafael Peier](https://unsplash.com/photos/northern-lights-illuminate-a-starry-sky-over-snowy-mountains-XXX2uavaR38) | `XXX2uavaR38` |
| Snowy Mountains | [Michiel Annaert](https://unsplash.com/photos/a-snowy-mountain-range-cCjUaIo1m50) | `cCjUaIo1m50` |
| Autumn Woodland | [Johannes Plenio](https://unsplash.com/photos/autumn-trees-H3_GQYwcyH8) | `H3_GQYwcyH8` |
| Lavender Sunset | [Léonard Cotte](https://unsplash.com/photos/lavender-field-c1Jp-fo53U8) | `c1Jp-fo53U8` |
| Desert Dunes | [Jules Bassoleil](https://unsplash.com/photos/a-desert-landscape-with-sand-dunes-gpX3TRNDf4E) | `gpX3TRNDf4E` |
| Coastal Cliffs | [Kamsin Kaneko](https://unsplash.com/photos/coastal-cliffs-overlooking-a-calm-blue-ocean-bay-aG5eXfboJzk) | `aG5eXfboJzk` |

## Preparation and verification

Images are 1920 × 1080, progressively encoded JPEG at quality 86 with 4:2:0 chroma subsampling. EXIF orientation is applied and `ImageOps.fit` crops to 16:9 without stretching. Metadata is removed. Separate 384 × 216 JPEG thumbnails use quality 78. `nature-manifest.json` records exact byte lengths, SHA-256 hashes, source dimensions, crop positions and interface-area luminance samples. Source downloads are high-resolution Unsplash CDN JPEGs requested at a maximum width of 4000 pixels; they are not claimed to be the full camera originals. Those intermediate files are not published.

Mountain Lake, Iceland Waterfall and Desert Dunes are portrait originals. Their landscape crops necessarily omit part of the original view. The Mountain Lake crop is moved upward to preserve the peaks and reflection; the Waterfall crop retains the upper cascade. Other images use a centred crop. All ten final images and thumbnails were visually inspected together in `nature-contact-sheet.jpg`.

Bright Tropical Beach water, Autumn Woodland sunlight and Lavender Sunset sky require the launcher’s text/icon shadow and focus treatment. No interface elements are burned into the photographs. Physical TV contrast remains a separate device test.

With Pillow installed, reproduce from the reviewed source records:

```sh
python3 tools/prepare-nature-wallpapers.py --sources nature-sources.json --source-cache /tmp/karnaros-nature-source-cache --output . --download
python3 tools/playlist-v2.py --check
python3 tools/playlist.py --check
```

PNG/JPEG encoding may vary with Pillow/libjpeg versions. Regenerate the manifest and version 2 catalog together whenever changing image bytes. Keep the legacy `playlist.json`, `catalog.json` and `videos/stillwater.mp4` unchanged for existing launchers.
