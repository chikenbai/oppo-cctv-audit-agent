#!/usr/bin/env python3
"""
Optimized Helper Utilities for OPPO Indonesia SST CCTV Audit Agent:
1. Two-stage keyframe pre-seek (`-ss <pre> -i ... -ss <offset>`) for 10x faster clean HEVC frame & 10fps grid extraction without gray P-frame artifacts.
2. Auto-timestamped overview contact sheet extraction (`fps=1/2` with burned-in `T=%{pts:hms} (%{pts}s)` on every tile).
3. Red bounding box + red-background text label + bottom banner annotation.
4. Direct 1-step upload to branch Google Drive folder (`gdrive mutate upload --parent <BRANCH_FOLDER_ID>`).
"""

import os
import re
import subprocess
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def extract_overview_grids(
    video_path: str,
    out_dir: str,
    prefix: str = "overview",
    fps_expr: str = "1/2",
    tile_w: int = 640,
    tile_h: int = 360,
    cols: int = 3,
    rows: int = 4,
    pre_seek_sec: float = 0.0,
    duration_sec: float | None = None,
) -> list[str]:
    """
    Extract high-clarity overview contact sheets with burned-in timestamp (seconds & HMS)
    on every tile so the agent can immediately identify exact interaction seconds.
    Default 3x4 grid at 640x360 per tile -> 1920x1440 per sheet (24 seconds per sheet at fps=1/2).
    """
    os.makedirs(out_dir, exist_ok=True)
    out_pattern = os.path.join(out_dir, f"{prefix}_%03d.jpg")

    cmd = ["ffmpeg", "-y", "-threads", "0"]
    if pre_seek_sec > 0:
        cmd += ["-ss", f"{pre_seek_sec:.2f}"]
    cmd += ["-i", video_path]
    if duration_sec is not None:
        cmd += ["-t", f"{duration_sec:.2f}"]

    drawtext_filter = (
        f"drawtext=fontfile={FONT_PATH}:"
        f"text='t=%{{eif\\:t+{int(pre_seek_sec)}\\:d}}s (%{{pts\\:hms\\:{int(pre_seek_sec)}}})':"
        f"x=10:y=h-th-10:fontsize=24:fontcolor=yellow:box=1:boxcolor=black@0.75:boxborderw=4"
    )
    vf = f"fps={fps_expr},scale={tile_w}:{tile_h},{drawtext_filter},tile={cols}x{rows}"
    cmd += ["-vf", vf, "-q:v", "3", out_pattern]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return sorted(
        os.path.join(out_dir, f)
        for f in os.listdir(out_dir)
        if f.startswith(f"{prefix}_") and f.endswith(".jpg")
    )


def extract_clean_frame(
    video_path: str,
    timestamp_sec: float,
    out_path: str,
    pre_roll: float = 4.0,
) -> None:
    """
    Extract a clean full-HD frame from HEVC/MP4 without gray keyframe artifacts.
    Uses `-ss <ts - pre_roll>` before `-i` to jump to a nearby keyframe in <1s,
    and `-vf trim=start=<accurate_offset>` to decode cleanly to the exact target frame.
    """
    fast_seek = max(0.0, timestamp_sec - pre_roll)
    accurate_offset = timestamp_sec - fast_seek
    cmd = [
        "ffmpeg", "-y", "-threads", "0",
        "-ss", f"{fast_seek:.3f}",
        "-i", video_path,
        "-vf", f"trim=start={accurate_offset:.3f}:duration=0.2,setpts=PTS-STARTPTS",
        "-frames:v", "1", "-q:v", "2", out_path
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def extract_10fps_verification_grid(
    video_path: str,
    start_sec: float,
    duration_sec: float,
    crop_w: int,
    crop_h: int,
    crop_x: int,
    crop_y: int,
    out_path: str,
    tile: str = "4x4",
    fps: float = 5.0,
    tile_w: int = 450,
    tile_h: int = 400,
    pre_roll: float = 4.0,
) -> None:
    """
    Extract a high-resolution 4x4 close-up verification grid (450x400 per tile = 1800x1600 total,
    max 16 frames per image) with burned-in 0.1s timestamps so hands and objects are crystal clear.
    NEVER use 8x10 or 10x10 grids (which shrink tiles too small and cause false-positive C3 hallucinations).
    """
    fast_seek = max(0.0, start_sec - pre_roll)
    accurate_offset = start_sec - fast_seek
    drawtext_filter = (
        f"drawtext=fontfile={FONT_PATH}:"
        f"text='%{{eif\\:t+{int(start_sec)}\\:d}}.%{{eif\\:mod(t*10\\,10)\\:d}}s':"
        f"x=10:y=10:fontsize=28:fontcolor=yellow:box=1:boxcolor=black@0.8:boxborderw=5"
    )
    vf = (
        f"trim=start={accurate_offset:.3f}:duration={duration_sec:.3f},setpts=PTS-STARTPTS,"
        f"fps={fps},crop={crop_w}:{crop_h}:{crop_x}:{crop_y},scale={tile_w}:{tile_h},"
        f"{drawtext_filter},tile={tile}"
    )
    cmd = [
        "ffmpeg", "-y", "-threads", "0",
        "-ss", f"{fast_seek:.3f}",
        "-i", video_path,
        "-vf", vf,
        "-frames:v", "1", "-q:v", "2", out_path
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def annotate_violation(
    src_path: str,
    out_path: str,
    boxes: list[tuple[int, int, int, int, str, int, int]],
    banner_text: str,
) -> None:
    """
    Draw red bounding boxes, red-background text labels, and a bottom banner on a frame.
    Each item in `boxes` is: (x1, y1, x2, y2, label_text, label_x, label_y).
    """
    img = Image.open(src_path).convert("RGB")
    draw = ImageDraw.Draw(img, "RGBA")
    width, height = img.size

    font_label = ImageFont.truetype(FONT_PATH, 26)
    font_banner = ImageFont.truetype(FONT_PATH, 24)

    for (x1, y1, x2, y2, label, lx, ly) in boxes:
        draw.rectangle([x1, y1, x2, y2], outline=(255, 0, 0, 255), width=5)
        bbox = draw.textbbox((lx, ly), label, font=font_label)
        pad = 6
        draw.rectangle(
            [bbox[0] - pad, bbox[1] - pad, bbox[2] + pad, bbox[3] + pad],
            fill=(220, 0, 0, 230)
        )
        draw.text((lx, ly), label, fill=(255, 255, 255, 255), font=font_label)

    draw.rectangle([0, height - 56, width, height], fill=(0, 0, 0, 210))
    draw.text((20, height - 44), banner_text, fill=(255, 230, 0, 255), font=font_banner)

    img.save(out_path, quality=92)


def upload_to_branch_folder(local_image_path: str, branch_folder_id: str) -> str:
    """Upload annotated screenshot directly into the branch folder in 1 API call."""
    out = subprocess.check_output(
        ["gdrive", "mutate", "upload", local_image_path, "--parent", branch_folder_id],
        text=True
    )
    match = re.search(r"\(ID:\s*([^)]+)\)", out)
    if not match:
        raise RuntimeError(f"Could not parse file ID from gdrive output: {out}")
    return match.group(1).strip()
