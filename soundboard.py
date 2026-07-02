#!/usr/bin/env python3
import os
import subprocess
import tkinter as tk
from PIL import Image, ImageTk
# Direct framebuffer display
os.putenv('SDL_VIDEODRIVER', 'fbcon')
os.putenv('SDL_FBDEV', '/dev/fb0')
os.putenv('SDL_MOUSEDRV', 'TSLIB')
os.putenv('SDL_MOUSEDEV', '/dev/input/event0')

# -------- CONFIG --------
ICON_DIR = "/home/cameron/icons"
SOUND_DIR = "/home/cameron/sounds"
PODCAST_SCRIPT = "/home/cameron/audio/podcast.py"
COMMLINK_SCRIPT = "/home/cameron/RPM-Commlink/commlink.py"

MAP_IMAGE = "/home/cameron/Pictures/Las-Vegas-Map-Feature.jpg"

WINDOW_WIDTH = 280
WINDOW_HEIGHT = 600
ICON_SIZE = 60
VOLUME = 50   # percent
GRID_PAD_X = 3
GRID_PAD_Y = 3
# ------------------------

SOUNDS = [
    ("map.png", "growl.mp3"),  # <-- opens map
    ("cartoon.png", "grappling-gun.mp3"),
    ("explosion.png", "explosion-fx-343683.mp3"),
    ("fart.png", "wet-fart-335478.mp3"),
    ("jet.png", "jet.mp3"),
    ("lasergun.png", "laser-gun-81720.mp3"),
    ("marshall.png", "marshall-paw-patrol-ringtone.mp3"),
    ("pawpatrol.png", "extreme.mp3"),
    ("racing-car.png", "engine.mp3"),
    ("transmission.png", "sneeze.mp3"),
    ("batman.png", "Batman.mp3"),
    ("punch.png", "Punch.mp3"),
]

# ---------- SOUNDBOARD ----------

class SoundBoard:
    def __init__(self, root):
        self.root = root
        self.root.title("Sound Board")
        self.root.configure(bg="green")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.attributes("-fullscreen", True)
        self.images = []
        self.build_ui()

    def play_sound(self, filename):
        path = os.path.join(SOUND_DIR, filename)
        subprocess.Popen(
            ["mpv", "--no-video", f"--volume={VOLUME}", path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def launch_map(self):
        self.root.destroy()
        MapWindow()

    def launch_podcast(self):
        subprocess.Popen(["python3", PODCAST_SCRIPT])
        self.exit_app()

    def launch_commlink(self):
        self.root.destroy()
        subprocess.Popen(["python3", COMMLINK_SCRIPT])

    def exit_app(self):
        self.root.attributes("-fullscreen", False)
        self.root.destroy()
        subprocess.Popen(["openbox", "--restart"],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def build_ui(self):
        frame = tk.Frame(self.root, bg="green")
        frame.pack(expand=True)
        row, col = 0, 0
        for icon, sound in SOUNDS:
            img = Image.open(os.path.join(ICON_DIR, icon))
            img = img.resize((ICON_SIZE, ICON_SIZE), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.images.append(photo)

            #cmd = self.launch_map if icon == "map.png" else lambda s=sound: self.play_sound(s)
            if icon == "map.png":
                cmd = self.launch_map
            elif icon == "pawpatrol.png":
                cmd = self.launch_commlink
            else:
                cmd = lambda s=sound: self.play_sound(s) 

            btn = tk.Button(frame, image=photo, bg="green", borderwidth=0,
                            width=ICON_SIZE, height=ICON_SIZE,
                            highlightthickness=0, command=cmd)
            btn.grid(row=row, column=col, padx=GRID_PAD_X, pady=GRID_PAD_Y)

            col += 1
            if col == 3:
                col = 0
                row += 1

        tk.Button(frame, text="Podcast", font=("Arial", 18, "bold"),
                  width=5, height=2, command=self.launch_podcast).grid(row=4, column=0, pady=20)

        tk.Button(frame, text="Exit", font=("Arial", 18),
                  width=5, height=2, bg="red", fg="white",
                  command=self.exit_app).grid(row=4, column=2, pady=20)

# ---------- MAP WINDOW WITH PAN + TAP ZOOM ----------

class MapWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Map")
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg="black")

        # Canvas for pan/zoom
        self.canvas = tk.Canvas(self.root, bg="black")
        self.canvas.pack(fill="both", expand=True)

        # Load original image
        self.img_orig = Image.open(MAP_IMAGE)
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        self.scale = min(screen_w / self.img_orig.width, screen_h / self.img_orig.height)
        self.current_scale = self.scale

        self.img_resized = self.img_orig.resize(
            (int(self.img_orig.width*self.current_scale),
             int(self.img_orig.height*self.current_scale)),
            Image.LANCZOS
        )
        self.tk_img = ImageTk.PhotoImage(self.img_resized)
        self.img_id = self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img)

        # Hidden exit hotspot
        exit_btn = tk.Button(self.root, text="", command=self.close_map,
                             bg="black", activebackground="black", bd=0)
        exit_btn.place(x=0, y=0, width=80, height=80)

        # Zoom / drag state
        self.zoomed_in = False
        self.drag_data = {"x": 0, "y": 0, "item_x": 0, "item_y": 0}

        # Bind events
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        self.root.mainloop()

    def on_button_press(self, event):
        # Start drag data
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
        coords = self.canvas.coords(self.img_id)
        self.drag_data["item_x"] = coords[0]
        self.drag_data["item_y"] = coords[1]
        self.drag_data["moved"] = False

    def on_drag(self, event):
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        if self.zoomed_in:
            new_x = self.drag_data["item_x"] + dx
            new_y = self.drag_data["item_y"] + dy
            self.canvas.coords(self.img_id, new_x, new_y)
            self.drag_data["moved"] = True

    def on_button_release(self, event):
        # Treat as tap if movement was very small
        moved = self.drag_data.get("moved", False)
        dx = abs(event.x - self.drag_data["x"])
        dy = abs(event.y - self.drag_data["y"])
        if not moved and dx < 5 and dy < 5:
            self.toggle_zoom()

    def toggle_zoom(self):
        if not self.zoomed_in:
            self.current_scale = self.scale * 2
            self.zoomed_in = True
        else:
            self.current_scale = self.scale
            self.zoomed_in = False
            self.canvas.coords(self.img_id, 0, 0)
        self.update_image()

    def update_image(self):
        new_w = int(self.img_orig.width * self.current_scale)
        new_h = int(self.img_orig.height * self.current_scale)
        img_resized = self.img_orig.resize((new_w, new_h), Image.LANCZOS)
        self.tk_img = ImageTk.PhotoImage(img_resized)
        self.canvas.itemconfig(self.img_id, image=self.tk_img)

    def close_map(self):
        self.root.destroy()
        subprocess.Popen(["python3", "/home/cameron/soundboard.py"])

# ---------- MAIN ----------

if __name__ == "__main__":
    root = tk.Tk()
    SoundBoard(root)
    root.mainloop()
