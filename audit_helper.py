#!/usr/bin/env python3
"""
Helper utilities for OPPO Indonesia SST CCTV Audit Agent:
- Clean HEVC frame extraction (avoiding gray P-frame artifacts)
- Red bounding box + label + bottom banner annotation
- Uploading to Google Drive and moving into the branch folder
- Batch writing bilingual findings to Google Sheets
"""

import json
import os
import re
import subprocess
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def extract_clean_frame(video_path: str, timestamp_sec: float, out_path: str) -> None:
    """Extract a clean full-HD frame from HEVC/MP4 without gray keyframe artifacts."""
    cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-vf", f"trim=start={timestamp_sec}:duration=0.2,setpts=PTS-STARTPTS",
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
    tile: str = "5x4"
) -> None:
    """Extract a 10fps close-up verification grid (0.1s intervals) to verify C3/A2 interactions."""
    cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-vf", (
            f"trim=start={start_sec}:duration={duration_sec},setpts=PTS-STARTPTS,"
            f"fps=10,crop={crop_w}:{crop_h}:{crop_x}:{crop_y},tile={tile}"
        ),
        "-frames:v", "1", "-q:v", "2", out_path
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def annotate_violation(
    src_path: str,
    out_path: str,
    boxes: list[tuple[int, int, int, int, str, int, int]],
    banner_text: str
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
    """Upload annotated screenshot to Drive and move it into the branch folder."""
    out = subprocess.check_output(["gdrive", "mutate", "upload", local_image_path], text=True)
    match = re.search(r"\(ID:\s*([^)]+)\)", out)
    if not match:
        raise RuntimeError(f"Could not parse file ID from gdrive output: {out}")
    file_id = match.group(1).strip()
    subprocess.run(["gdrive", "mutate", "mv", file_id, branch_folder_id], check=True)
    return file_id
