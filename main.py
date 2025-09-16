import tkinter as tk
from tkinter import ttk
import sys

from mode_webcam import run_webcam
from mode_screen import run_screen
from mode_pip import run_pip

def start_screen():
    root.destroy()
    run_screen(target_fps=30)

def start_webcam():
    root.destroy()
    run_webcam(cam_index=0)

def start_pip():
    root.destroy()
    run_pip(target_fps=30, cam_index=0, pip_scale=0.22, margin=20)

def quit_app():
    root.destroy()
    sys.exit(0)

root = tk.Tk()
root.title("녹화 모드 선택")
root.geometry("360x220")
root.resizable(False, False)

frm = ttk.Frame(root, padding=16)
frm.pack(fill="both", expand=True)

ttk.Label(frm, text="원하는 녹화 모드를 선택하세요:", font=("Segoe UI", 11)).pack(anchor="w", pady=(0,10))

ttk.Button(frm, text="1) 컴퓨터 화면 녹화", command=start_screen).pack(fill="x", pady=6, ipady=6)
ttk.Button(frm, text="2) 웹캠 녹화", command=start_webcam).pack(fill="x", pady=6, ipady=6)
ttk.Button(frm, text="3) 화면 + 우하단 웹캠(PiP) 녹화", command=start_pip).pack(fill="x", pady=6, ipady=6)

sep = ttk.Separator(frm, orient="horizontal")
sep.pack(fill="x", pady=8)

ttk.Button(frm, text="종료", command=quit_app).pack(side="right")

root.mainloop()