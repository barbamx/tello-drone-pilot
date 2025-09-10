from textual.app import App, ComposeResult
from textual.widgets import Button, Static, Header, Footer
from textual.containers import Container, Horizontal
from textual.reactive import reactive
from textual import events
import threading
import time
from tello.tello import Tello


class TelloStats(Static):
    battery = reactive("?")
    speed = reactive("?")
    height = reactive("?")

    def render(self):
        return f"Battery: {self.battery}%    Speed: {self.speed} cm/s    Altitude: {self.height} cm"


class TelloGUIController(App):
    CSS_PATH = None

    def __init__(self):
        super().__init__()
        self.tello = Tello()
        self.movement_distance = 20
        self.movement_interval = 0.15
        self.is_flying = False
        self.stats_widget = TelloStats()
        self._stop_stats = False
        self._move_threads = {}
        self._move_active = {}
        self.init_tello()
        self.start_stats_polling()

    def compose(self) -> ComposeResult:
        yield Header()
        yield self.stats_widget
        yield Container(
            Horizontal(
                Button("Takeoff", id="takeoff", variant="success"),
                Button("Land", id="land", variant="warning"),
                Button("Emergency", id="emergency", variant="error"),
            ),
            Horizontal(
                Button("Up", id="up"),
                Button("Down", id="down"),
                Button("Left", id="left"),
                Button("Right", id="right"),
                Button("Forward", id="forward"),
                Button("Back", id="back"),
            ),
            Static(
                "Controls: [T]akeoff, [L]and, [E]mergency, Arrows/WASD for movement, [Q]uit",
                id="help",
            ),
        )
        yield Footer()

    def init_tello(self):
        threading.Thread(target=self._init_tello_thread, daemon=True).start()

    def _init_tello_thread(self):
        self.tello.send_command("command")
        time.sleep(2)

    def start_stats_polling(self):
        def poll():
            while not self._stop_stats:
                self._update_stats()
                time.sleep(2)

        threading.Thread(target=poll, daemon=True).start()

    def _update_stats(self):
        try:
            battery = self._query_stat("battery?")
            speed = self._query_stat("speed?")
            height = self._query_stat("height?")
            if battery is not None:
                self.stats_widget.battery = battery
            if speed is not None:
                self.stats_widget.speed = speed
            if height is not None:
                self.stats_widget.height = height
        except Exception as e:
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

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id
        if btn_id == "takeoff":
            self.takeoff()
        elif btn_id == "land":
            self.land()
        elif btn_id == "emergency":
            self.emergency()
        elif btn_id in {"up", "down", "left", "right", "forward", "back"}:
            self.move(btn_id)

    async def on_key(self, event: events.Key) -> None:
        key = event.key.lower()
        if key == "t":
            self.takeoff()
        elif key == "l":
            self.land()
        elif key == "e":
            self.emergency()
        elif key in {"up", "down", "left", "right"}:
            self.move(key)
        elif key == "w":
            self.move("forward")
        elif key == "s":
            self.move("back")
        elif key == "a":
            self.move("left")
        elif key == "d":
            self.move("right")
        elif key == "q":
            await self.action_quit()

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

    async def on_shutdown(self, event):
        self._stop_stats = True


if __name__ == "__main__":
    TelloGUIController().run()
