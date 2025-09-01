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

        # Initialize connection
        print("Initializing Tello connection...")
        self.tello.send_command("command")
        time.sleep(2)

        print("Tello Keyboard Controller Ready!")
        print("Controls:")

    print("  ENTER       - Takeoff")
    print("  DEL         - Land")
    print("  UP Arrow    - Move up 20cm")
    print("  DOWN Arrow  - Move down 20cm")
    print("  LEFT Arrow  - Move left 20cm")
    print("  RIGHT Arrow - Move right 20cm")
    print("  W           - Move front 20cm")
    print("  S           - Move back 20cm")
    print("  SPACE       - Emergency stop")
    print("  ESC         - Exit")
    print("\nPress keys to control the drone...")

    def handle_key(self, e):
        """Handle key press events using keyboard library"""
        try:
            if e.name == "enter":
                print("ENTER pressed - Sending takeoff command")
                self.tello.send_command("takeoff")
            elif e.name == "delete":
                print("DEL pressed - Sending land command")
                self.tello.send_command("land")
            elif e.name == "up":
                print("UP pressed - Move up 20cm")
                self.tello.send_command("up 20")
            elif e.name == "down":
                print("DOWN pressed - Move down 20cm")
                self.tello.send_command("down 20")
            elif e.name == "left":
                print("LEFT pressed - Move left 20cm")
                self.tello.send_command("left 20")
            elif e.name == "right":
                print("RIGHT pressed - Move right 20cm")
                self.tello.send_command("right 20")
            elif e.name == "w":
                print("W pressed - Move front 20cm")
                self.tello.send_command("forward 20")
            elif e.name == "s":
                print("S pressed - Move back 20cm")
                self.tello.send_command("back 20")
            elif e.name == "space":
                print("SPACE pressed - Emergency stop")
                self.tello.send_command("emergency")
            elif e.name == "esc":
                print("ESC pressed - Exiting program...")
                self.is_running = False
                keyboard.unhook_all()
        except Exception as ex:
            print(f"Error handling key press: {ex}")

    def run(self):
        """Main run loop with keyboard event hook"""
        try:
            keyboard.hook(self.handle_key)
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
