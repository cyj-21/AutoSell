import argparse
import time
from pathlib import Path

import numpy as np
import pydirectinput
import pyautogui
from PIL import Image


ROOT = Path(__file__).resolve().parent
BASELINE = ROOT / "baseline"
SCREENSHOTS = ROOT / "screenshout"

START_POS = (2300 / 2560, 1310 / 1440)
CLAIM_POS = (1545 / 2560, 1120 / 1440)
EXIT_POS = (70 / 2560, 70 / 1440)
LEVEL_POS = (230 / 2560, 1110 / 1440)
BEGIN_REGION = (2100 / 2560, 1240 / 1440, 380 / 2560, 130 / 1440)
FINISH_REGION = (1320 / 2560, 1060 / 1440, 460 / 2560, 140 / 1440)
ENERGY_PER_ROUND = 12
THRESHOLD = 0.72
TIMEOUT = 30
INTERVAL = 1
STAGE_SECONDS = 53
ROUND_WAIT = 3


def rect(size, region):
    w, h = size
    x, y, rw, rh = region
    return round(w * x), round(h * y), round(w * rw), round(h * rh)


def crop(img, region):
    x, y, w, h = rect(img.size, region)
    return img.crop((x, y, x + w, y + h))


def shot(label, region):
    SCREENSHOTS.mkdir(exist_ok=True)
    img = pyautogui.screenshot(region=rect(pyautogui.size(), region)).convert("RGB")
    img.save(SCREENSHOTS / f"{label}.png")
    return img


def score(a, b):
    if a.size != b.size:
        b = b.resize(a.size)
    a = np.asarray(a.resize((320, 180)).convert("L"), dtype=np.float32)
    b = np.asarray(b.resize((320, 180)).convert("L"), dtype=np.float32)
    return 1 - np.sqrt(np.mean((a - b) ** 2)) / 255


def load_baseline(name, region):
    img = Image.open(BASELINE / f"{name}.png").convert("RGB")
    return crop(img, region) if img.width > 1000 else img


def wait_page(name, baseline, region, threshold, timeout, interval):
    end = time.time() + timeout
    while time.time() < end:
        s = score(shot(f"check_{name}", region), baseline)
        print(name, "score:", round(s, 3))
        if s >= threshold:
            return
        time.sleep(interval)
    raise TimeoutError(f"wait {name} timeout")


def click_pos(pos):
    w, h = pyautogui.size()
    pydirectinput.click(round(w * pos[0]), round(h * pos[1]))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("energy", nargs="?", type=int, help="current energy")
    p.add_argument("reserve", nargs="?", type=int, help="energy to keep")
    args = p.parse_args()

    energy = args.energy if args.energy is not None else int(input("current energy: "))
    reserve = args.reserve if args.reserve is not None else int(input("energy to keep: "))
    loops = max(0, (energy - reserve) // ENERGY_PER_ROUND)
    if loops == 0:
        print("no rounds to run")
        return

    pyautogui.FAILSAFE = True
    pydirectinput.PAUSE = 0.1
    baselines = {
        "begin": load_baseline("begin", BEGIN_REGION),
        "finish": load_baseline("finish", FINISH_REGION),
    }
    regions = {
        "begin": BEGIN_REGION,
        "finish": FINISH_REGION,
    }

    print("start after 3s; move mouse to top-left to stop")
    print(f"energy={energy}, reserve={reserve}, rounds={loops}")
    time.sleep(3)

    for i in range(loops):
        print(f"round {i + 1}/{loops}")
        click_pos(LEVEL_POS)
        wait_page("begin", baselines["begin"], regions["begin"], THRESHOLD, TIMEOUT, INTERVAL)
        click_pos(START_POS)
        time.sleep(STAGE_SECONDS)
        click_pos(EXIT_POS)
        wait_page("finish", baselines["finish"], regions["finish"], THRESHOLD, TIMEOUT, INTERVAL)
        click_pos(CLAIM_POS)
        time.sleep(ROUND_WAIT)

    print("done")


if __name__ == "__main__":
    main()
