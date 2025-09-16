import os
import time
import cv2 as cv
from utils import ensure_outdir, ts_name, draw_rec_indicator, show_help, window_closed

def run_webcam(cam_index: int = 0):
    window = "Webcam (Space:Record/Stop, ESC:Exit)"
    cv.namedWindow(window, cv.WINDOW_NORMAL)

    cap = cv.VideoCapture(cam_index, cv.CAP_DSHOW) if os.name == "nt" else cv.VideoCapture(cam_index)
    if not cap.isOpened():
        print("웹캠을 열 수 없습니다.")
        return

    fps = cap.get(cv.CAP_PROP_FPS)
    if not fps or fps <= 1.0:
        fps = 30.0
    w = int(cap.get(cv.CAP_PROP_FRAME_WIDTH)) or 640
    h = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT)) or 480
    size = (w, h)

    out_dir = ensure_outdir()
    writer = None
    recording = False
    t0 = 0.0

    show_help(window)
    print("웹캠 모드 시작")

    while True:
        ok, frame = cap.read()
        if not ok:
            print("프레임 읽기 실패")
            break

        if recording:
            if writer is None:
                fourcc = cv.VideoWriter_fourcc(*"mp4v")
                out_path = out_dir / ts_name("webcam")
                writer = cv.VideoWriter(str(out_path), fourcc, fps, size)
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

        if key == 27:  # ESC
            print("종료")
            break
        elif key == 32:  # Space
            recording = not recording
            if not recording and writer is not None:
                writer.release()
                writer = None
                print("녹화 중지")

    if writer is not None:
        writer.release()
    cap.release()
    cv.destroyWindow(window)