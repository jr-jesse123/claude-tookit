#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["imageio-ffmpeg", "pillow"]
# ///
"""Pack one Playwright MCP trace into a self-contained zip and a captioned video.

The MCP writes every trace of a session into one shared folder (trace-<id>.trace,
trace-<id>.network, resources/, screencast/). Only the files a trace cites are
copied, so the zip never carries another trace's files.

    pack-trace.py <trace-id|path-to-.trace> --out <dir> --name <case> [--traces-dir DIR] [--video]

The zip and the action list are always written; the captioned video only with --video.
"""
import argparse
import json
import re
import subprocess
import sys
import tempfile
import zipfile
from collections import Counter
from pathlib import Path

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

USER_ACTIONS = {"goto", "click", "fill", "press", "selectOption", "hover", "check", "uncheck", "setInputFiles", "dragAndDrop", "type"}
SECRET_LABEL = re.compile(r"password|secret|token", re.I)
SHA1 = re.compile(r"\b[0-9a-f]{40}\b")
CAPTION_SECONDS = 2.0


def locate(arg: str, traces_dir: Path) -> Path:
    candidate = Path(arg)
    if candidate.suffix == ".trace" and candidate.exists():
        return candidate
    found = traces_dir / f"trace-{arg}.trace"
    if not found.exists():
        sys.exit(f"trace not found: {found}")
    return found


def describe(params: dict) -> str:
    selector = params.get("selector", "")
    match = re.search(r'internal:describe="(.*)"', selector)
    return match.group(1) if match else selector.split(">>")[0].strip()


def caption(event: dict) -> str:
    method, params = event["method"], event.get("params") or {}
    label = describe(params)
    if method == "goto":
        return "Navigate: " + re.sub(r"^https?://[^/]+", "", params.get("url", ""))
    if method == "fill":
        value = "••••••••" if SECRET_LABEL.search(label) else params.get("value", "")
        return f"Type in {label}: {value}"
    if method == "press":
        return f"Press {params.get('key', '')} in {label}" if label else f"Press {params.get('key', '')}"
    return f"{method[0].upper()}{method[1:]}: {label}"


def load(trace: Path):
    events = [json.loads(line) for line in trace.read_text().splitlines() if line.strip()]
    actions = [(e["startTime"], caption(e)) for e in events if e["type"] == "before" and e.get("method") in USER_ACTIONS]
    frames = sorted((e["timestamp"], e["file"], e["width"], e["height"]) for e in events if e["type"] == "screencast-frame")
    viewports = Counter(
        (e["snapshot"]["viewport"]["width"], e["snapshot"]["viewport"]["height"])
        for e in events if e["type"] == "frame-snapshot" and e["snapshot"].get("isMainFrame"))
    viewport = viewports.most_common(1)[0][0] if viewports else None
    return actions, frames, viewport


def pack_zip(trace: Path, network: Path, frames, zip_path: Path) -> None:
    resources_dir = trace.parent / "resources"
    cited = set(SHA1.findall(trace.read_text() + network.read_text()))
    present = {p.name: p for p in resources_dir.iterdir() if p.stem in cited}
    skipped = len(list(resources_dir.iterdir())) - len(present)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(trace, "trace.trace")
        z.write(network, "trace.network")
        for name, path in present.items():
            z.write(path, f"resources/{name}")
        missing = 0
        for _, rel, _, _ in frames:
            source = trace.parent / rel
            if source.exists():
                z.write(source, rel)
            else:
                missing += 1
    print(f"zip: {len(present)} resources, {len(frames) - missing} frames; left out {skipped} unrelated resources in the folder; {missing} frames missing")


def font(size: int):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def build_video(trace: Path, actions, frames, viewport, video_path: Path, cap: float) -> None:
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    label_font = font(22)
    with tempfile.TemporaryDirectory() as tmp:
        images = []
        for _, rel, window_width, window_height in frames:
            image = Image.open(trace.parent / rel).convert("RGB")
            if viewport and (viewport[0] < window_width or viewport[1] < window_height):
                # The screencast covers the whole browser window; the page occupies its top-left viewport.
                scale = image.width / window_width
                image = image.crop((0, 0, min(round(viewport[0] * scale), image.width), min(round(viewport[1] * scale), image.height)))
            images.append(image)
        target = Counter(image.size for image in images).most_common(1)[0][0]
        lines = []
        for index, (stamp, _, _, _) in enumerate(frames):
            image = images[index] if images[index].size == target else images[index].resize(target)
            current = [text for start, text in actions if 0 <= stamp - start <= CAPTION_SECONDS * 1000]
            if current:
                draw = ImageDraw.Draw(image, "RGBA")
                height = 40
                draw.rectangle([0, image.height - height, image.width, image.height], fill=(0, 0, 0, 190))
                draw.text((12, image.height - height + 8), current[-1][:90], fill=(255, 255, 255, 255), font=label_font)
            out = Path(tmp) / f"{index:05d}.jpg"
            image.save(out, quality=88)
            following = (frames[index + 1][0] - stamp) / 1000 if index + 1 < len(frames) else 1.0
            lines.append(f"file '{out}'\nduration {min(max(following, 0.04), cap):.3f}")
        lines.append(f"file '{out}'")
        listing = Path(tmp) / "list.txt"
        listing.write_text("\n".join(lines))
        subprocess.run(
            [ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(listing),
             "-vf", "fps=15,scale=trunc(iw/2)*2:trunc(ih/2)*2", "-c:v", "libvpx-vp9", "-crf", "32", "-b:v", "0", "-an", str(video_path)],
            check=True, capture_output=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("trace")
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--name", required=True)
    parser.add_argument("--traces-dir", type=Path, default=Path(".playwright-mcp/traces"))
    parser.add_argument("--video", action="store_true", help="also build the captioned screencast video")
    parser.add_argument("--idle-cap", type=float, default=1.5, help="longest time one frame stays on screen, in seconds")
    args = parser.parse_args()

    trace = locate(args.trace, args.traces_dir)
    network = trace.with_suffix(".network")
    args.out.mkdir(parents=True, exist_ok=True)
    actions, frames, viewport = load(trace)
    zip_path, video_path = args.out / f"{args.name}.trace.zip", args.out / f"{args.name}.webm"
    pack_zip(trace, network, frames, zip_path)
    if args.video:
        build_video(trace, actions, frames, viewport, video_path, args.idle_cap)
        print(f"video: {video_path} ({len(frames)} frames)")
    (args.out / f"{args.name}.actions.txt").write_text(
        "\n".join(f"{(start - frames[0][0]) / 1000:7.1f}s  {text}" for start, text in actions) + "\n")


if __name__ == "__main__":
    main()
