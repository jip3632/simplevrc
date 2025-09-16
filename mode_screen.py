import time
import numpy as np
import cv2 as cv
from utils import ensure_outdir, ts_name, draw_rec_indicator, show_help, window_closed

try:
    import mss
except ImportError:
    mss = None

def run_screen(target_fps: int = 30, monitor_index: int = 1):
    if mss is None:
        print("mss 가 없습니다. conda install -c conda-forge mss 로 설치하세요.")
        return

    window = "Screen (Space:Record/Stop, ESC:Exit)"
    cv.namedWindow(window, cv.WINDOW_NORMAL)

    sct = mss.mss()
    if monitor_index >= len(sct.monitors):
        print(f"모니터 인덱스 {monitor_index} 가 범위를 벗어났습니다. 1 사용.")
        monitor_index = 1
    mon = sct.monitors[monitor_index]
    W, H = mon["width"], mon["height"]
    bbox = {"top": mon["top"], "left": mon["left"], "width": W, "height": H}

    out_dir = ensure_outdir()
    fourcc = cv.VideoWriter_fourcc(*"mp4v")
    writer = None
    recording = False
    t0 = 0.0

    show_help(window)
    print(f"화면 모드 시작: {W}x{H} @ {target_fps}fps")

    frame_interval = 1.0 / target_fps
    prev = time.time()

    while True:
        # 목표 FPS에 맞춰 슬립
        now = time.time()
        if now - prev < frame_interval:
            time.sleep(max(0, frame_interval - (now - prev)))
        prev = time.time()

        img = np.array(sct.grab(bbox))
        frame = cv.cvtColor(img, cv.COLOR_BGRA2BGR)

        if recording:
            if writer is None:
                out_path = out_dir / ts_name("screen")
                writer = cv.VideoWriter(str(out_path), fourcc, target_fps, (W, H))
                if not writer.isOpened():
                    print("VideoWriter 생성 실패")
                    recording = False
                else:
                    t0 = time.time()
                    print(f"녹화 시작: {out_path}")
            if writer is not None:
                writer.write(frame)
                draw_rec_indicator(frame, t0)

        cv.imshow(window, frame)
        key = cv.waitKey(1) & 0xFF
        if window_closed(window):
            print("창이 닫혀 종료합니다.")
            break

        if key == 27:
            print("종료")
            break
        elif key == 32:
            recording = not recording
            if not recording and writer is not None:
                writer.release()
                writer = None
                print("녹화 중지")

    if writer is not None:
        writer.release()
    cv.destroyWindow(window)