import threading
import time
from tello.tello import Tello

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock

# For video streaming
import cv2
import numpy as np
from kivy.graphics.texture import Texture
from kivy.uix.image import Image


class TelloGUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self.tello = Tello()
        self.movement_distance = 20
        self.movement_interval = 0.15
        self.is_flying = False
        self._stop_stats = False

        # Video stream attributes
        self.video_streaming = False
        self.capture = None

        # Status display
        self.status_label = Label(
            text="Battery: ?  Speed: ?  Altitude: ?",
            size_hint=(1, 0.1),
            font_size=18,
        )
        self.add_widget(self.status_label)

        # Navigation grid
        nav_grid = GridLayout(
            cols=3,
            rows=4,
            size_hint=(1, 0.6),
            spacing=10,
            padding=10,
        )

        nav_grid.add_widget(Label())  # Empty
        btn_up = Button(text="Up", font_size=20)
        btn_up.bind(on_press=lambda _: self.move("up"))
        nav_grid.add_widget(btn_up)
        nav_grid.add_widget(Label())  # Empty

        btn_left = Button(text="Left", font_size=20)
        btn_left.bind(on_press=lambda _: self.move("left"))
        nav_grid.add_widget(btn_left)

        btn_forward = Button(text="Forward", font_size=20)
        btn_forward.bind(on_press=lambda _: self.move("forward"))
        nav_grid.add_widget(btn_forward)

        btn_right = Button(text="Right", font_size=20)
        btn_right.bind(on_press=lambda _: self.move("right"))
        nav_grid.add_widget(btn_right)

        nav_grid.add_widget(Label())  # Empty
        btn_down = Button(text="Down", font_size=20)
        btn_down.bind(on_press=lambda _: self.move("down"))
        nav_grid.add_widget(btn_down)
        nav_grid.add_widget(Label())  # Empty

        btn_back = Button(text="Back", font_size=20)
        btn_back.bind(on_press=lambda _: self.move("back"))
        nav_grid.add_widget(Label())  # Empty
        nav_grid.add_widget(btn_back)
        nav_grid.add_widget(Label())  # Empty

        self.add_widget(nav_grid)

        # Control buttons
        control_box = BoxLayout(
            orientation="horizontal",
            size_hint=(1, 0.15),
            spacing=10,
            padding=10,
        )
        btn_takeoff = Button(
            text="Takeoff",
            background_color=(0, 1, 0, 1),
            font_size=20,
        )
        btn_takeoff.bind(on_press=lambda _: self.takeoff())
        btn_land = Button(
            text="Land",
            background_color=(1, 0.7, 0, 1),
            font_size=20,
        )
        btn_land.bind(on_press=lambda _: self.land())
        btn_emergency = Button(
            text="Emergency",
            background_color=(1, 0, 0, 1),
            font_size=20,
        )
        btn_emergency.bind(on_press=lambda _: self.emergency())

        # Video button
        btn_video = Button(
            text="Start Video",
            background_color=(0.2, 0.5, 1, 1),
            font_size=20,
        )
        btn_video.bind(on_press=lambda _: self.toggle_video())

        control_box.add_widget(btn_takeoff)
        control_box.add_widget(btn_land)
        control_box.add_widget(btn_emergency)
        control_box.add_widget(btn_video)
        self.add_widget(control_box)

        # Help label
        self.add_widget(
            Label(
                text="Use the buttons for navigation and control.\nStatus updates every 2s.",
                size_hint=(1, 0.15),
                font_size=14,
            )
        )

        # Video display
        self.video_image = Image(size_hint=(1, 0.5))
        self.add_widget(self.video_image)

        # Initialize Tello and start stats polling
        threading.Thread(target=self._init_tello_thread, daemon=True).start()
        Clock.schedule_interval(lambda dt: self._update_stats(), 2)

    def _init_tello_thread(self):
        self.tello.send_command("command")
        time.sleep(2)

    def _update_stats(self, *args):
        try:
            battery = self._query_stat("battery?")
            speed = self._query_stat("speed?")
            height = self._query_stat("height?")
            self.status_label.text = f"Battery: {battery or '?'}  Speed: {speed or '?'}  Altitude: {height or '?'}"
        except Exception:
            pass

    def _query_stat(self, cmd):
        try:
            self.tello.send_command(cmd)
            time.sleep(0.5)
            log = self.tello.get_log()
            for stat in reversed(log):
                if stat.command == cmd and stat.response is not None:
                    resp = stat.response
                    if isinstance(resp, bytes):
                        resp = resp.decode(errors="ignore")
                    return resp.strip()
        except Exception:
            pass
        return None

    def move(self, direction):
        cmd = f"{direction} {self.movement_distance}"
        threading.Thread(
            target=self.tello.send_command, args=(cmd,), daemon=True
        ).start()

    def takeoff(self):
        threading.Thread(
            target=self.tello.send_command, args=("takeoff",), daemon=True
        ).start()
        self.is_flying = True

    def land(self):
        threading.Thread(
            target=self.tello.send_command, args=("land",), daemon=True
        ).start()
        self.is_flying = False

    def emergency(self):
        threading.Thread(
            target=self.tello.send_command, args=("emergency",), daemon=True
        ).start()

    def toggle_video(self):
        if not self.video_streaming:
            threading.Thread(target=self.start_video_stream, daemon=True).start()
        else:
            self.stop_video_stream()

    def start_video_stream(self):
        self.tello.send_command("streamon")
        time.sleep(1)
        self.capture = cv2.VideoCapture("udp://0.0.0.0:11111")
        self.video_streaming = True
        Clock.schedule_interval(self.update_video_frame, 1 / 30)

    def stop_video_stream(self):
        self.video_streaming = False
        if self.capture:
            self.capture.release()
            self.capture = None
        self.video_image.texture = None

    def update_video_frame(self, dt):
        if not self.video_streaming or not self.capture:
            return
        ret, frame = self.capture.read()
        if ret:
            # Convert BGR to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            buf = frame.tobytes()
            texture = Texture.create(
                size=(frame.shape[1], frame.shape[0]), colorfmt="rgb"
            )
            texture.blit_buffer(buf, colorfmt="rgb", bufferfmt="ubyte")
            self.video_image.texture = texture
        else:
            # If frame not received, stop video
            self.stop_video_stream()


class TelloKivyApp(App):
    def build(self):
        return TelloGUI()


if __name__ == "__main__":
    TelloKivyApp().run()
