# FireFrame Wallpapers

Original video backgrounds for the FireFrame Fire TV launcher. The initial playlist contains **Stillwater**, a quiet, animated color field made specifically for FireFrame.

Configure this public playlist URL in FireFrame Settings:

```text
https://raw.githubusercontent.com/RedRocDev/FireFrame-Wallpapers/main/playlist.json
```

FireFrame downloads and verifies the selected video, then caches it for offline playback. The source repository is [RedRocDev/FireFrame-Wallpapers](https://github.com/RedRocDev/FireFrame-Wallpapers).

## Included artwork

| Video | Format | Duration | Credits | License |
| --- | --- | --- | --- | --- |
| `videos/stillwater.mp4` | 1920 × 1080, H.264 High, yuv420p, 30 FPS, no audio | 8 seconds | FireFrame original procedural artwork | MIT |

Stillwater uses a periodic mathematical color field, generated with FFmpeg. It contains no third-party photograph, recording, music, logos or other source media. It is copied from FireFrame's original bundled sample, with its reproducible recipe in `tools/generate-stillwater.sh`. FFmpeg is a development tool and is not included here.

All current artwork, helper code and metadata use the [MIT license](LICENSE). Preserve that license and these credits when redistributing them. Future submissions must include permission to redistribute the video; do not add third-party media solely because it is available to download.

## Update the playlist

Use Python 3.10 or newer. No Python packages or GitHub token are required for local preparation.

1. Add an owned or appropriately licensed `.mp4` under `videos/`.
2. Add its ID, title, file, credit and license to `catalog.json`.
3. Generate `playlist.json`, then verify it against the actual files:

   ```sh
   python3 tools/playlist.py
   python3 tools/playlist.py --check
   ```

4. Commit both the video and generated playlist, then push the same commit.

The helper computes exact byte sizes and SHA-256 checksums, verifies the MP4 `ftyp` signature, rejects duplicate IDs and files outside `videos/`, and enforces FireFrame's playlist/file limits. It does not download content or contact GitHub. The default URLs use `main`; for immutable video references, regenerate with `--ref YOUR_VIDEO_COMMIT_SHA` after the video commit exists remotely.

Use `ffprobe` to inspect newly added clips. Prefer 1920 × 1080 SDR H.264, yuv420p, 30 FPS, no audio and a modest bitrate. A looping player does not make arbitrary footage visually seamless; join the first and last frames deliberately and test the result on the Fire TV.

Regenerate the original sample only when FFmpeg with the `libx264` encoder is installed:

```sh
sh tools/generate-stillwater.sh
python3 tools/playlist.py
python3 tools/playlist.py --check
```

Encoding output can differ between FFmpeg versions. Always regenerate the checksum and byte length after changing the binary.

## Future public video hosting

The JSON playlist can stay on GitHub while future MP4 files live on a public HTTPS video host. FireFrame versions with **Trusted video hosts** in Settings require each exact external hostname to be added manually; the external host list starts empty. Trust does not extend to subdomains or redirect hosts automatically. Use stable, public HTTPS `.mp4` URLs with no embedded credentials, query strings, expiring signatures or custom ports. Each entry still needs the exact byte length and SHA-256 checksum. A downloaded playlist cannot grant trust to a hostname.

Wasabi or another public object store can be considered later. **No Wasabi bucket has been provisioned, no external video host is configured by this repository, and the current Stillwater video is served by GitHub.**

`tools/playlist.py` currently reads a local-file `catalog.json` and generates GitHub raw video URLs. It does not provision storage, upload videos to external hosts or generate external-host entries. A future external-host playlist must be prepared separately or use an updated generator; the current `--check` command verifies the local GitHub-generated playlist and will reject manual URL changes. Keep the original licensed video bytes, checksum and size together when moving a video.

## Publish updates

Every committed file in this repository is public. Verify ownership and licensing before adding media. Clone the existing repository rather than creating a second one:

```sh
git clone https://github.com/RedRocDev/FireFrame-Wallpapers.git
cd FireFrame-Wallpapers
python3 tools/playlist.py --check
```

After editing, regenerate the playlist, run the checks, commit and push with an account permitted to update this repository. Verify the published playlist and MP4 after each change. Keep `playlist.json` and the referenced video bytes consistent so checksum validation succeeds.
