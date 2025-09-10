import time
import os
from tello.tello import Tello
from evdev import InputDevice, categorize, ecodes, list_devices


class SteamDeckController:
    def __init__(self):
        self.tello = Tello()
        self.is_running = True
        self.takeoff_sent = False

        # Find Steam Deck input device (you may need to adjust this)
        self.device = self.find_steamdeck_device()
        if not self.device:
            print("Steam Deck input device not found.")
            exit(1)

        print("Initializing Tello connection...")
        self.tello.send_command("command")
        time.sleep(2)
        print("Tello Steam Deck Controller Ready!")
        self.print_controls()

    def find_steamdeck_device(self):
        # Try to find a device with 'Steam' or 'Gamepad' in its name
        for dev_path in list_devices():
            dev = InputDevice(dev_path)
            if "Steam" in dev.name or "Gamepad" in dev.name or "Deck" in dev.name:
                print(f"Using input device: {dev.name} ({dev_path})")
                return InputDevice(dev_path)
        return None

    def print_controls(self):
        print("Controls:")
        print("  D-pad UP         - Takeoff")
        print("  Right Trackpad   - Move drone (up/down/left/right)")
        print("  D-pad DOWN       - Land")
        print("  D-pad LEFT       - Emergency stop")
        print("  D-pad RIGHT      - Exit")
        print("\nUse Steam Deck controls to fly the drone...")

    def handle_event(self, event):
        # D-pad events (ABS_HAT0Y: up/down, ABS_HAT0X: left/right)
        if event.type == ecodes.EV_ABS:
            if event.code == ecodes.ABS_HAT0Y:
                if event.value == -1 and not self.takeoff_sent:  # D-pad up
                    print("D-pad UP pressed - Sending takeoff command")
                    self.tello.send_command("takeoff")
                    self.takeoff_sent = True
                elif event.value == 1:  # D-pad down
                    print("D-pad DOWN pressed - Sending land command")
                    self.tello.send_command("land")
            elif event.code == ecodes.ABS_HAT0X:
                if event.value == -1:  # D-pad left
                    print("D-pad LEFT pressed - Emergency stop")
                    self.tello.send_command("emergency")
                elif event.value == 1:  # D-pad right
                    print("D-pad RIGHT pressed - Exiting program...")
                    self.is_running = False

        # Right trackpad events (ABS_RX, ABS_RY)
        elif event.type == ecodes.EV_ABS:
            # These codes may vary; adjust as needed for your device
            if event.code == ecodes.ABS_RX:
                if event.value < 120:  # Move left
                    print("Trackpad: Move left")
                    self.tello.send_command("left 20")
                elif event.value > 136:  # Move right
                    print("Trackpad: Move right")
                    self.tello.send_command("right 20")
            elif event.code == ecodes.ABS_RY:
                if event.value < 120:  # Move up
                    print("Trackpad: Move up")
                    self.tello.send_command("up 20")
                elif event.value > 136:  # Move down
                    print("Trackpad: Move down")
                    self.tello.send_command("down 20")

    def run(self):
        try:
            for event in self.device.read_loop():
                if not self.is_running:
                    break
                self.handle_event(event)
        except KeyboardInterrupt:
            print("\nKeyboard interrupt received")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.cleanup()

    def cleanup(self):
        print("Cleaning up...")
        self.is_running = False
        try:
            self.tello.send_command("land")
        except:
            pass
        log = self.tello.get_log()
        if log:
            timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
            try:
                os.makedirs("log", exist_ok=True)
                with open(f"log/steamdeck_control_{timestamp}.txt", "w") as out:
                    for stat in log:
                        out.write(stat.return_stats())
                print(f"Log saved to: log/steamdeck_control_{timestamp}.txt")
            except Exception as e:
                print(f"Error saving log: {e}")


if __name__ == "__main__":
    controller = SteamDeckController()
    controller.run()
