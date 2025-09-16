import time
from datetime import datetime
from pathlib import Path

import cv2 as cv

def ensure_outdir() -> Path:
    out_dir = Path(__file__).parent / "records"
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir

def ts_name(prefix="record", suffix=".mp4") -> str:
    return f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{suffix}"

def draw_rec_indicator(frame, start_time: float):
    elapsed = int(time.time() - start_time) if start_time > 0 else 0
    mm, ss = divmod(elapsed, 60)
    cv.circle(frame, (30, 30), 10, (0, 0, 255), -1)  # 빨간 원
    cv.putText(frame, f"REC {mm:02d}:{ss:02d}", (50, 40),
               cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2, cv.LINE_AA)

def show_help(window_name: str):
    try:
        cv.displayOverlay(window_name, "Space: 녹화 시작/정지 | ESC: 종료", 2000)
    except Exception:
        pass

def window_closed(window_name: str) -> bool:
    try:
        v = cv.getWindowProperty(window_name, cv.WND_PROP_VISIBLE)
    except cv.error:
        return True
    return (v < 1) 