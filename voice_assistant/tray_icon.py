import tkinter as tk
from PIL import Image, ImageTk
import threading
import time

class TrayIconTk:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Assistant Icon")
        self.root.geometry("64x64+20+20")  # Положение и размер
        self.root.overrideredirect(True)  # Без рамки
        self.root.attributes("-topmost", True)  # Поверх всех окон

        self.icon_label = tk.Label(self.root)
        self.icon_label.pack()

        self.icons = {
            "idle": ImageTk.PhotoImage(Image.open("icon_idle.png").resize((64, 64))),
            "active": ImageTk.PhotoImage(Image.open("icon_active.png").resize((64, 64)))
        }

        self.set_idle()

    def set_idle(self):
        self.icon_label.config(image=self.icons["idle"])

    def set_active(self):
        self.icon_label.config(image=self.icons["active"])

    def run(self):
        self.root.mainloop()
