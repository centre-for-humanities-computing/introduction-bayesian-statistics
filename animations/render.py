"""Render the three concept animations: MP4 (slides), GIF (notebooks) and a poster frame.

    uv run python animations/render.py                  # all three, with `hyperframes render`
    uv run python animations/render.py 02_repeat_the_study
    uv run python animations/render.py --via-snapshots  # fallback, see below

Requires Node.js 22+ and FFmpeg. HyperFrames is run with npx (pinned version) and
downloads its own headless Chrome on first use.

`--via-snapshots` captures every frame with `hyperframes snapshot` and encodes them
with FFmpeg. It gives the same frames, for machines where `hyperframes render`
cannot start its local server (e.g. sandboxes that forbid binding to 127.0.0.1).
"""

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
RENDERS = HERE / "renders"
HYPERFRAMES = ["npx", "--yes", "hyperframes@0.9.29"]
FPS = 30

# animation -> (duration in s, time in s of the poster frame shown before playback)
ANIMATIONS = {
    "01_where_data_come_from": (25, 21.0),
    "02_repeat_the_study": (25, 23.0),
    "03_holding_constant": (30, 24.0),
}
GIF_FILTER = (
    "fps=12,scale=960:-1:flags=lanczos,split[a][b];"
    "[a]palettegen=max_colors=96:stats_mode=diff[p];"
    "[b][p]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle"
)


def run(cmd, **kw):
    print("  $", " ".join(str(c) for c in cmd)[:160])
    subprocess.run(cmd, check=True, **kw)


def render_mp4(project: Path, out: Path) -> None:
    run(
        [
            *HYPERFRAMES,
            "render",
            str(project),
            "-o",
            str(out),
            "--fps",
            str(FPS),
            "--quiet",
        ]
    )


def render_mp4_via_snapshots(project: Path, out: Path, duration: float) -> None:
    n = round(FPS * duration)
    with tempfile.TemporaryDirectory() as tmp:
        times = ",".join(f"{i / FPS:.5f}" for i in range(n))
        run(
            [*HYPERFRAMES, "snapshot", "--at", times, "--timeout", "120000", "-o", tmp],
            cwd=project,
        )
        frames = sorted(
            Path(tmp).glob("frame-*.png"),
            key=lambda p: float(re.search(r"at-([0-9.]+)s", p.name).group(1)),
        )
        if len(frames) != n:
            sys.exit(f"expected {n} frames, got {len(frames)}")
        for i, f in enumerate(frames):
            f.rename(Path(tmp) / f"seq_{i:04d}.png")
        run(
            [
                "ffmpeg",
                "-y",
                "-loglevel",
                "error",
                "-framerate",
                str(FPS),
                "-i",
                str(Path(tmp) / "seq_%04d.png"),
                "-c:v",
                "libx264",
                "-preset",
                "slow",
                "-crf",
                "16",
                "-pix_fmt",
                "yuv420p",
                "-movflags",
                "+faststart",
                str(out),
            ]
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "names",
        nargs="*",
        help=f"animations to render (default: all): {', '.join(ANIMATIONS)}",
    )
    parser.add_argument(
        "--via-snapshots",
        action="store_true",
        help="capture frames with snapshot + ffmpeg",
    )
    args = parser.parse_args()
    unknown = set(args.names) - set(ANIMATIONS)
    if unknown:
        parser.error(f"unknown animation(s): {', '.join(sorted(unknown))}")
    for tool in ("npx", "ffmpeg"):
        if shutil.which(tool) is None:
            sys.exit(f"`{tool}` not found: install Node.js 22+ and FFmpeg")

    run([sys.executable, str(HERE / "make_data.py")])
    RENDERS.mkdir(exist_ok=True)
    for name in args.names or ANIMATIONS:
        print(f"\n== {name}")
        mp4, gif, poster = (
            RENDERS / f"{name}{ext}" for ext in (".mp4", ".gif", "_poster.png")
        )
        duration, poster_time = ANIMATIONS[name]
        if args.via_snapshots:
            render_mp4_via_snapshots(HERE / name, mp4, duration)
        else:
            render_mp4(HERE / name, mp4)
        run(
            [
                "ffmpeg",
                "-y",
                "-loglevel",
                "error",
                "-i",
                str(mp4),
                "-vf",
                GIF_FILTER,
                "-loop",
                "0",
                str(gif),
            ]
        )
        run(
            [
                "ffmpeg",
                "-y",
                "-loglevel",
                "error",
                "-ss",
                str(poster_time),
                "-i",
                str(mp4),
                "-frames:v",
                "1",
                str(poster),
            ]
        )
        for f in (mp4, gif, poster):
            print(
                f"  wrote {f.relative_to(HERE.parent)} ({f.stat().st_size / 1e6:.1f} MB)"
            )


if __name__ == "__main__":
    main()
