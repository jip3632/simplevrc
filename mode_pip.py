import os
import time
import numpy as np
import cv2 as cv
from utils import ensure_outdir, ts_name, draw_rec_indicator, show_help, window_closed

try:
    import mss
except ImportError:
    mss = None

def run_pip(target_fps: int = 30, cam_index: int = 0, pip_scale: float = 0.22, margin: int = 20, monitor_index: int = 1):
    if mss is None:
        print("mss 가 없습니다. conda install -c conda-forge mss 로 설치하세요.")
        return

    window = "Screen + Webcam (Space:Record/Stop, ESC:Exit)"
    cv.namedWindow(window, cv.WINDOW_NORMAL)

    # 화면
    sct = mss.mss()
    if monitor_index >= len(sct.monitors):
        print(f"모니터 인덱스 {monitor_index} 가 범위를 벗어났습니다. 1 사용.")
        monitor_index = 1
    mon = sct.monitors[monitor_index]
    W, H = mon["width"], mon["height"]
    bbox = {"top": mon["top"], "left": mon["left"], "width": W, "height": H}

    # 웹캠
    cap = cv.VideoCapture(cam_index, cv.CAP_DSHOW) if os.name == "nt" else cv.VideoCapture(cam_index)
    if not cap.isOpened():
        print("웹캠을 열 수 없습니다.")
        return

    out_dir = ensure_outdir()
    fourcc = cv.VideoWriter_fourcc(*"mp4v")
    writer = None
    recording = False
    t0 = 0.0

    show_help(window)
    print(f"화면+웹캠 모드 시작: 캔버스 {W}x{H} @ {target_fps}fps, PiP scale={pip_scale}")

    frame_interval = 1.0 / target_fps
    prev = time.time()

    while True:
        # 목표 FPS
        now = time.time()
        if now - prev < frame_interval:
            time.sleep(max(0, frame_interval - (now - prev)))
        prev = time.time()

        # 1) 화면 프레임
        screen_np = np.array(sct.grab(bbox))
        canvas = cv.cvtColor(screen_np, cv.COLOR_BGRA2BGR)

        # 2) 웹캠 프레임
        ok, cam_frame = cap.read()
        if ok:
            ph = int(H * pip_scale)
            pw = int(cam_frame.shape[1] * (ph / cam_frame.shape[0]))
            pip = cv.resize(cam_frame, (pw, ph), interpolation=cv.INTER_AREA)

            # 3) 우하단 배치
            x2 = W - margin
            y2 = H - margin
            x1 = x2 - pw
            y1 = y2 - ph

            # 반투명 테두리 배경
            overlay = canvas.copy()
            cv.rectangle(overlay, (x1-6, y1-6), (x2+6, y2+6), (0, 0, 0), -1)
            canvas = cv.addWeighted(overlay, 0.3, canvas, 0.7, 0)

            canvas[y1:y2, x1:x2] = pip

        if recording:
            if writer is None:
                out_path = out_dir / ts_name("pip")
                writer = cv.VideoWriter(str(out_path), fourcc, target_fps, (W, H))
                if not writer.isOpened():
                    print("VideoWriter 생성 실패")
                    recording = False
                else:
                    t0 = time.time()
                    print(f"녹화 시작: {out_path}")
            if writer is not None:
                writer.write(canvas)
                draw_rec_indicator(canvas, t0)

        cv.imshow(window, canvas)
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
    cap.release()
    cv.destroyWindow(window)