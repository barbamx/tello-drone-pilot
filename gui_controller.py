import customtkinter as ctk
import threading
import time
from tello.tello import Tello


class TelloGUIController:
    def __init__(self, master):
        self.master = master
        self.tello = Tello()
        self.movement_distance = 20
        self.movement_interval = 0.15
        self.is_flying = False
        self._move_threads = {}
        self._move_active = {}
        ctk.set_appearance_mode("dark")  # Modern dark mode
        ctk.set_default_color_theme("blue")
        self.init_tello()
        self.create_widgets()

    def init_tello(self):
        threading.Thread(target=self._init_tello_thread, daemon=True).start()

    def _init_tello_thread(self):
        self.tello.send_command("command")
        time.sleep(2)

    def create_widgets(self):
        self.master.title("Tello Drone GUI Controller")
        self.master.geometry("420x380")
        frame = ctk.CTkFrame(self.master)
        frame.pack(expand=True, fill="both", padx=20, pady=20)

        btn_takeoff = ctk.CTkButton(
            frame,
            text="Takeoff",
            command=self.takeoff,
            width=120,
            height=40,
            fg_color="#43ea7a",
            text_color="black",
            corner_radius=12,
        )
        btn_land = ctk.CTkButton(
            frame,
            text="Land",
            command=self.land,
            width=120,
            height=40,
            fg_color="#ffb347",
            text_color="black",
            corner_radius=12,
        )
        btn_up = ctk.CTkButton(frame, text="Up", width=100, height=36, corner_radius=12)
        btn_down = ctk.CTkButton(
            frame, text="Down", width=100, height=36, corner_radius=12
        )
        btn_left = ctk.CTkButton(
            frame, text="Left", width=100, height=36, corner_radius=12
        )
        btn_right = ctk.CTkButton(
            frame, text="Right", width=100, height=36, corner_radius=12
        )
        btn_forward = ctk.CTkButton(
            frame, text="Forward", width=100, height=36, corner_radius=12
        )
        btn_back = ctk.CTkButton(
            frame, text="Back", width=100, height=36, corner_radius=12
        )
        btn_emergency = ctk.CTkButton(
            frame,
            text="Emergency",
            command=self.emergency,
            width=120,
            height=40,
            fg_color="#e74c3c",
            text_color="white",
            corner_radius=12,
        )

        # Bind long-press events for movement buttons
        self._bind_long_press(btn_up, "up")
        self._bind_long_press(btn_down, "down")
        self._bind_long_press(btn_left, "left")
        self._bind_long_press(btn_right, "right")
        self._bind_long_press(btn_forward, "forward")
        self._bind_long_press(btn_back, "back")

        # Layout with grid for modern look
        btn_takeoff.grid(row=0, column=0, padx=10, pady=10, columnspan=2, sticky="ew")
        btn_land.grid(row=0, column=2, padx=10, pady=10, columnspan=2, sticky="ew")
        btn_up.grid(row=1, column=1, padx=10, pady=10)
        btn_down.grid(row=3, column=1, padx=10, pady=10)
        btn_left.grid(row=2, column=0, padx=10, pady=10)
        btn_right.grid(row=2, column=2, padx=10, pady=10)
        btn_forward.grid(row=2, column=1, padx=10, pady=10)
        btn_back.grid(row=4, column=1, padx=10, pady=10)
        btn_emergency.grid(row=5, column=0, columnspan=3, padx=10, pady=20, sticky="ew")

    def _bind_long_press(self, button, direction):
        button.bind("<ButtonPress-1>", lambda e: self._start_continuous_move(direction))
        button.bind(
            "<ButtonRelease-1>", lambda e: self._stop_continuous_move(direction)
        )

    def _start_continuous_move(self, direction):
        if self._move_active.get(direction):
            return
        self._move_active[direction] = True
        t = threading.Thread(
            target=self._continuous_move_thread, args=(direction,), daemon=True
        )
        self._move_threads[direction] = t
        t.start()

    def _stop_continuous_move(self, direction):
        self._move_active[direction] = False

    def _continuous_move_thread(self, direction):
        while self._move_active.get(direction, False):
            self.move(direction)
            time.sleep(self.movement_interval)

    def move(self, direction):
        cmd = f"{direction} {self.movement_distance}"
        print(f"Sending: {cmd}")
        threading.Thread(
            target=self.tello.send_command, args=(cmd,), daemon=True
        ).start()

    def takeoff(self):
        print("Takeoff")
        threading.Thread(
            target=self.tello.send_command, args=("takeoff",), daemon=True
        ).start()
        self.is_flying = True

    def land(self):
        print("Land")
        threading.Thread(
            target=self.tello.send_command, args=("land",), daemon=True
        ).start()
        self.is_flying = False

    def emergency(self):
        print("Emergency")
        threading.Thread(
            target=self.tello.send_command, args=("emergency",), daemon=True
        ).start()


if __name__ == "__main__":
    root = ctk.CTk()
    app = TelloGUIController(root)
    root.mainloop()
