import sys
import threading
import time
import os
from tello.tello import Tello
import keyboard


class TelloKeyboardController:
    def __init__(self):
        self.tello = Tello()
        self.is_running = True
        self.active_keys = set()
        self.movement_threads = {}
        self.movement_commands = {
            "up": "up 20",
            "down": "down 20",
            "left": "left 20",
            "right": "right 20",
            "w": "forward 20",
            "s": "back 20",
        }
        self.movement_interval = 0.15  # seconds between repeated commands

        # Initialize connection
        print("Initializing Tello connection...")
        self.tello.send_command("command")
        time.sleep(2)

        print("Tello Keyboard Controller Ready!")
        print("Controls:")
        print("  ENTER       - Takeoff")
        print("  DEL         - Land")
        print("  UP Arrow    - Move up 20cm (hold for continuous)")
        print("  DOWN Arrow  - Move down 20cm (hold for continuous)")
        print("  LEFT Arrow  - Move left 20cm (hold for continuous)")
        print("  RIGHT Arrow - Move right 20cm (hold for continuous)")
        print("  W           - Move front 20cm (hold for continuous)")
        print("  S           - Move back 20cm (hold for continuous)")
        print("  SPACE       - Emergency stop")
        print("  ESC         - Exit")
        print("\nPress keys to control the drone...")

    def handle_key(self, event):
        """Handle key press events using keyboard library (continuous movement)"""
        try:
            name = event.name
            if event.event_type == "down":
                if name in self.movement_commands and name not in self.active_keys:
                    self.active_keys.add(name)
                    t = threading.Thread(
                        target=self._continuous_move, args=(name,), daemon=True
                    )
                    self.movement_threads[name] = t
                    t.start()
                elif name == "enter":
                    print("ENTER pressed - Sending takeoff command")
                    self.tello.send_command("takeoff")
                elif name == "delete":
                    print("DEL pressed - Sending land command")
                    self.tello.send_command("land")
                elif name == "space":
                    print("SPACE pressed - Emergency stop")
                    self.tello.send_command("emergency")
                elif name == "esc":
                    print("ESC pressed - Exiting program...")
                    self.is_running = False
                    return False
            elif event.event_type == "up":
                if name in self.active_keys:
                    self.active_keys.remove(name)
        except Exception as e:
            print(f"Error handling key press: {e}")

    def _continuous_move(self, key_name):
        """Send movement command repeatedly while key is held down."""
        try:
            while self.is_running and key_name in self.active_keys:
                print(
                    f"{key_name.upper()} held - Sending {self.movement_commands[key_name]}"
                )
                self.tello.send_command(self.movement_commands[key_name])
                time.sleep(self.movement_interval)
        except Exception as e:
            print(f"Error in continuous movement thread: {e}")

    def run(self):
        """Main run loop with keyboard event handler (continuous movement)"""
        try:
            keyboard.hook(self.handle_key, suppress=False)
            while self.is_running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nKeyboard interrupt received")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.cleanup()

    def cleanup(self):
        """Cleanup resources"""
        print("Cleaning up...")
        self.is_running = False

        # Send land command as safety measure
        try:
            self.tello.send_command("land")
        except:
            pass

        # Get and save log
        log = self.tello.get_log()
        if log:
            timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
            try:
                os.makedirs("log", exist_ok=True)
                with open(f"log/keyboard_control_{timestamp}.txt", "w") as out:
                    for stat in log:
                        log_string = stat.return_stats()
                        out.write(log_string)
                print(f"Log saved to: log/keyboard_control_{timestamp}.txt")
            except Exception as e:
                print(f"Error saving log: {e}")


if __name__ == "__main__":
    controller = TelloKeyboardController()
    controller.run()
