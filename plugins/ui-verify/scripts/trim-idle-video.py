#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "imageio-ffmpeg"]
# ///
"""Cuts the idle stretches out of a Playwright recording, keeping every frame where anything moves.

A frame is "active" when enough pixels changed against the previous one. The thresholds are
low enough to catch the mouse cursor (a few dozen pixels) and above the codec noise of a
still page (a few pixels). Each active frame is padded so the viewer sees what led to the
action and has time to read the result.

With one input it writes <name>-short.webm next to it. With several inputs and -o it trims each
one and joins them in the order given into one file (the size of the first input is used; the
others are scaled to it), so one case that was recorded in parts becomes one video.
"""
import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import imageio_ffmpeg
import numpy as np

WIDTH, HEIGHT = 640, 360


def activity(ffmpeg: str, path: Path, fps: float, strong_delta: int, mid_delta: int):
    proc = subprocess.Popen(
        [ffmpeg, "-v", "error", "-i", str(path), "-vf", f"scale={WIDTH}:{HEIGHT},format=gray", "-f", "rawvideo", "-"],
        stdout=subprocess.PIPE,
    )
    previous, strong, mid = None, [], []
    while True:
        raw = proc.stdout.read(WIDTH * HEIGHT)
        if len(raw) < WIDTH * HEIGHT:
            break
        frame = np.frombuffer(raw, np.uint8).astype(np.int16)
        if previous is None:
            strong.append(0)
            mid.append(0)
        else:
            diff = np.abs(frame - previous)
            strong.append(int((diff > strong_delta).sum()))
            mid.append(int((diff > mid_delta).sum()))
        previous = frame
    return np.array(strong), np.array(mid)


def keep_segments(active: np.ndarray, fps: float, pad_before: float, pad_after: float):
    total = len(active) / fps
    segments = []
    for index in np.flatnonzero(active):
        start = max(0.0, index / fps - pad_before)
        end = min(total, index / fps + pad_after)
        if segments and start <= segments[-1][1]:
            segments[-1][1] = max(segments[-1][1], end)
        else:
            segments.append([start, end])
    return segments, total


def video_size(ffmpeg: str, path: Path) -> tuple[int, int]:
    probe = subprocess.run([ffmpeg, "-hide_banner", "-i", str(path)], capture_output=True, text=True)
    match = re.search(r"Video:.*?, (\d{2,5})x(\d{2,5})", probe.stderr)
    if not match:
        raise RuntimeError(f"cannot read the size of {path}")
    return int(match.group(1)), int(match.group(2))


def trim(ffmpeg: str, source: Path, output: Path, args) -> bool:
    strong, mid = activity(ffmpeg, source, args.fps, 40, 12)
    active = (strong >= args.min_strong) | (mid >= args.min_mid)
    segments, total = keep_segments(active, args.fps, args.pad_before, args.pad_after)
    if not segments:
        print(f"{source}: no motion found; nothing to keep", file=sys.stderr)
        return False

    kept = sum(end - start for start, end in segments)
    print(f"{source}: {total:.1f}s -> {kept:.1f}s, {len(segments)} segments kept, {int(active.sum())} active frames")
    for start, end in segments:
        print(f"  keep {start:6.2f}s - {end:6.2f}s")

    expression = "+".join(f"between(t,{start:.3f},{end:.3f})" for start, end in segments)
    subprocess.run(
        [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i", str(source),
         "-vf", f"select='{expression}',setpts=N/FRAME_RATE/TB", "-an",
         "-c:v", "libvpx", "-b:v", "400k", "-r", str(int(args.fps)), str(output)],
        check=True,
    )
    return True


def join(ffmpeg: str, parts: list[Path], output: Path, fps: float) -> None:
    width, height = video_size(ffmpeg, parts[0])
    inputs = [item for part in parts for item in ("-i", str(part))]
    scaled = "".join(f"[{i}:v]scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={int(fps)}[v{i}];" for i in range(len(parts)))
    chain = "".join(f"[v{i}]" for i in range(len(parts)))
    subprocess.run(
        [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", *inputs,
         "-filter_complex", f"{scaled}{chain}concat=n={len(parts)}:v=1:a=0[out]",
         "-map", "[out]", "-an", "-c:v", "libvpx", "-b:v", "400k", str(output)],
        check=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("inputs", type=Path, nargs="+", help="one recording, or the parts of one case in order (then -o is required)")
    parser.add_argument("-o", "--output", type=Path, help="output file; required with several inputs")
    parser.add_argument("--fps", type=float, default=25.0)
    parser.add_argument("--pad-before", type=float, default=0.7, help="seconds kept before an action")
    parser.add_argument("--pad-after", type=float, default=2.0, help="seconds kept after an action, to read the result")
    parser.add_argument("--min-strong", type=int, default=5, help="pixels changed by >40 levels that count as motion")
    parser.add_argument("--min-mid", type=int, default=40, help="pixels changed by >12 levels that count as motion")
    args = parser.parse_args()

    if len(args.inputs) > 1 and args.output is None:
        parser.error("several inputs need -o OUTPUT")

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    if len(args.inputs) == 1:
        source = args.inputs[0]
        output = args.output or source.with_name(source.stem + "-short.webm")
        if not trim(ffmpeg, source, output, args):
            return 1
        print(f"wrote {output}")
        return 0

    with tempfile.TemporaryDirectory() as folder:
        trimmed = []
        for index, source in enumerate(args.inputs):
            part = Path(folder) / f"part{index}.webm"
            if not trim(ffmpeg, source, part, args):
                return 1
            trimmed.append(part)
        join(ffmpeg, trimmed, args.output, args.fps)
    print(f"wrote {args.output} from {len(args.inputs)} parts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
