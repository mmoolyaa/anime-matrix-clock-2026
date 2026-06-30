from pathlib import Path
import subprocess
import signal
import sys
import time
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont
from pynput import keyboard

# ==========================
# CONFIG
# ==========================

BASE = Path(__file__).resolve().parent

FONT_PATH = BASE / "Hack-Regular.ttf"
FONT_SIZE = 16

WIDTH = 64
HEIGHT = 36

IMAGE_PATH = BASE / "file.png"

TIME_FORMAT = "%H:%M"
TEXT_COLOR = (255, 255, 255)
BACKGROUND_COLOR = (0, 0, 0)
MODE = "RGB"

KEYBIND = 269025089  # XF86Launch3

# ==========================

font = ImageFont.truetype(str(FONT_PATH), FONT_SIZE)
active = True


def run_asusctl(*args):
    """Run asusctl without raising an exception."""
    subprocess.run(
        ["asusctl", "anime", *args],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )


def enable_display(enable: bool):
    run_asusctl("--enable-display", "true" if enable else "false")


def render_clock():
    """Render the current time to a PNG."""
    now = datetime.now()
    text = now.strftime(TIME_FORMAT)

    img = Image.new(MODE, (WIDTH, HEIGHT), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(img)

    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]

    x = (WIDTH - w) // 2
    y = int((HEIGHT - h) / 1.1)

    draw.text(
        (x, y),
        text,
        fill=TEXT_COLOR,
        font=font,
    )

    img.save(IMAGE_PATH)


def update_display():
    render_clock()
    run_asusctl(
        "pixel-image",
        "--path",
        str(IMAGE_PATH),
    )


def cleanup(sig, frame):
    enable_display(False)
    sys.exit(0)


def on_press(key):
    global active

    try:
        vk = key.vk
    except AttributeError:
        vk = key.value.vk

    if vk == KEYBIND:
        active = not active

        enable_display(active)

        if active:
            update_display()


def main():
    enable_display(True)

    signal.signal(signal.SIGINT, cleanup)

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    last_time = None

    while True:
        if active:
            current = datetime.now().strftime(TIME_FORMAT)

            if current != last_time:
                last_time = current
                update_display()

        time.sleep(1)


if __name__ == "__main__":
    main()
