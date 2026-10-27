#!/bin/sh
# Original FireFrame color field. Frame n=0 and n=240 match mathematically;
# the 240-frame clip omits the duplicate end frame for normal loop cadence.
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
ffmpeg -hide_banner -loglevel error -f lavfi \
  -i 'nullsrc=s=1920x1080:r=30:d=8,geq=r=28+10*sin(2*PI*(X/W+T/8)):g=53+16*sin(2*PI*(X/W+Y/H+T/8)):b=63+12*sin(2*PI*(Y/H-T/8))' \
  -an -c:v libx264 -preset fast -crf 24 -pix_fmt yuv420p -profile:v high -level 4.1 \
  -movflags +faststart -y "$ROOT/videos/stillwater.mp4"
