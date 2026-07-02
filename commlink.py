import tkinter as tk
from PIL import Image, ImageTk, ImageEnhance
import pygame
import os
import random
import subprocess
import threading
import time

# -----------------------------
# CONFIG
# -----------------------------
BASE_PATH = "/home/cameron"

BG_IMAGE_PATH = "/home/cameron/icons/commlink.png"
SOUND_PATH = os.path.join(BASE_PATH, "sounds", "laser-gun-81720.mp3")
SOUNDBOARD_PATH = os.path.join(BASE_PATH, "soundboard.py")

STATUS_STREAM = [
    "COMM LINK STABLE",
    "DEEP SPACE SCAN ACTIVE",
    "SIGNAL INTERFERENCE LOW",
    "FREQUENCY LOCK MAINTAINED",
    "TRACKING SUBSPACE NOISE",
    "CHANNEL SYNC OK"
]

INCOMING_PRIORITY = [
    "!!! PRIORITY: UNKNOWN SIGNAL DETECTED",
    "!!! DISTRESS CALL RECEIVED FROM UNKNOWN ORIGIN",
    "!!! SIGNAL CORRUPTION EVENT DETECTED",
    "!!! ALL HANDS: SENSOR ANOMALY"
]

# -----------------------------
# AUDIO
# -----------------------------
pygame.mixer.init()

def play_sound():
    try:
        pygame.mixer.music.load(SOUND_PATH)
        pygame.mixer.music.play()
    except:
        pass


# -----------------------------
# MAIN APP
# -----------------------------
class CommlinkV4Clean:
    def __init__(self, root):
        self.root = root
        self.root.title("SHIP COMMS OS v4 CLEAN")
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg="black")

        self.canvas = tk.Canvas(root, highlightthickness=0, bg="black")
        self.canvas.pack(fill="both", expand=True)

        self.bg_id = None
        self.overlay_id = None

        self.load_background()
        
        # Get screen size parameters for right side placements
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        # -----------------------------
        # STATUS BAR
        # -----------------------------
        self.status_var = tk.StringVar()
        self.status_var.set("BOOTING SYSTEM...")

        self.status_label = tk.Label(
            root,
            textvariable=self.status_var,
            font=("Courier", 11, "bold"),
            fg="#00ff9c",
            bg="black"
        )
        # Position matching the upper left area of the UI card
        self.canvas.create_window(50, 50, anchor="nw", window=self.status_label)

        # -----------------------------
        # BOOT SEQUENCE
        # -----------------------------
        self.boot_msgs = [
            "[BOOT] Power core online",
            "[BOOT] Neural interface linked",
            "[BOOT] Comms array initializing",
            "[BOOT] Encryption lattice building",
            "[BOOT] SYSTEM ONLINE"
        ]
        self.boot_index = 0
        self.run_boot()

        # -----------------------------
        # BUTTONS (BOTTOM HUD BAR)
        # -----------------------------
        self.create_bottom_buttons()

        # -----------------------------
        # TERMINATE LINK BUTTON (RIGHT SIDE ALIGNED)
        # -----------------------------
        exit_btn = tk.Button(
            root,
            text="EXIT",
            font=("Courier", 8, "bold"),
            bg="red",
            fg="white",
            activebackground="darkred",
            activeforeground="white",
            width=6,
            height=6,
            padx=1,
            pady=1,
            command=self.exit_system
        )
        # Moves layout element to the right side of the screen matching your reference drawing
        self.canvas.create_window(screen_w - 60, 150, anchor="nw", window=exit_btn)

        # -----------------------------
        # THREADS
        # -----------------------------
        self.running = True
        threading.Thread(target=self.status_loop, daemon=True).start()
        threading.Thread(target=self.priority_loop, daemon=True).start()

    # -----------------------------
    # BACKGROUND (BLUE/GREEN HUD TONE)
    # -----------------------------
    def load_background(self):
        try:
            img = Image.open(BG_IMAGE_PATH).convert("RGB")

            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(1.4)

            self.original_bg = img
            self.render_bg(img)
        except Exception as e:
            print(f"BG error: {e}")

    def render_bg(self, img):
        self.bg_tk = ImageTk.PhotoImage(img)

        if self.bg_id:
            self.canvas.delete(self.bg_id)

        self.bg_id = self.canvas.create_image(0, 0, anchor="nw", image=self.bg_tk)

    def resize_bg(self, event):
        if hasattr(self, "original_bg"):
            resized = self.original_bg.resize((event.width, event.height))
            self.render_bg(resized)

    # -----------------------------
    # BOOT SEQUENCE
    # -----------------------------
    def run_boot(self):
        if self.boot_index < len(self.boot_msgs):
            self.status_var.set(self.boot_msgs[self.boot_index])
            self.boot_index += 1
            self.root.after(900, self.run_boot)
        else:
            self.status_var.set(">>> COMMS ONLINE <<<")

    # -----------------------------
    # BUTTON BAR (BOTTOM)
    # -----------------------------
    def create_bottom_buttons(self):
        self.buttons = []

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        frame = tk.Frame(self.root, bg="black")
        self.canvas.create_window(screen_w // 2, screen_h - 80, window=frame)

        for i in range(6):
            btn = tk.Button(
                frame,
                text=f"CH {i+1}",
                font=("Courier", 12, "bold"),
                bg="black",
                fg="#00ff9c",
                activebackground="#00ff9c",
                activeforeground="black",
                width=10,
                command=lambda i=i: self.channel_action(i)
            )
            btn.pack(side="left", padx=12)
            self.buttons.append(btn)

    # -----------------------------
    # CHANNEL ACTION
    # -----------------------------
    def channel_action(self, i):
        play_sound()
        self.flash_overlay(f"CHANNEL {i+1} ACTIVE")
        self.status_var.set(random.choice(STATUS_STREAM))

    # -----------------------------
    # OVERLAY
    # -----------------------------
    def flash_overlay(self, text):
        if self.overlay_id:
            self.canvas.delete(self.overlay_id)

        self.overlay_id = self.canvas.create_text(
            self.root.winfo_width() // 2,
            self.root.winfo_height() // 2,
            text=text,
            fill="#00ff9c",
            font=("Courier", 10, "bold")
        )

        self.root.after(1000, self.clear_overlay)

    def clear_overlay(self):
        if self.overlay_id:
            self.canvas.delete(self.overlay_id)
            self.overlay_id = None

    # -----------------------------
    # STATUS LOOP
    # -----------------------------
    def status_loop(self):
        while self.running:
            time.sleep(4)
            msg = random.choice(STATUS_STREAM)
            self.root.after(0, lambda m=msg: self.status_var.set(m))

    # -----------------------------
    # PRIORITY EVENTS
    # -----------------------------
    def priority_loop(self):
        while self.running:
            time.sleep(random.randint(8, 14))
            msg = random.choice(INCOMING_PRIORITY)
            self.root.after(0, lambda m=msg: self.status_var.set(m))

    # -----------------------------
    # EXIT SYSTEM
    # -----------------------------
    def exit_system(self):
        self.running = False
        try:
            subprocess.Popen(["python3", SOUNDBOARD_PATH])
        except:
            pass
        self.root.destroy()


# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = CommlinkV4Clean(root)
    root.mainloop()

