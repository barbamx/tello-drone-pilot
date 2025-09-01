import sys
import threading
import time
import os
from tello.tello import Tello
from pynput import keyboard


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

    def on_press(self, key):
        """Handle key press events"""
        try:
            if key == keyboard.Key.enter:
                print("ENTER pressed - Sending takeoff command")
                self.tello.send_command("takeoff")

            elif key == keyboard.Key.delete:
                print("DEL pressed - Sending land command")
                self.tello.send_command("land")

            elif key == keyboard.Key.up:
                print("UP pressed - Move up 20cm")
                self.tello.send_command("up 20")

            elif key == keyboard.Key.down:
                print("DOWN pressed - Move down 20cm")
                self.tello.send_command("down 20")

            elif key == keyboard.Key.left:
                print("LEFT pressed - Move left 20cm")
                self.tello.send_command("left 20")

            elif key == keyboard.Key.right:
                print("RIGHT pressed - Move right 20cm")
                self.tello.send_command("right 20")

            elif (
                hasattr(key, "char")
                and key.char is not None
                and key.char.lower() == "w"
            ):
                print("W pressed - Move front 20cm")
                self.tello.send_command("forward 20")

            elif (
                hasattr(key, "char")
                and key.char is not None
                and key.char.lower() == "s"
            ):
                print("S pressed - Move back 20cm")
                self.tello.send_command("back 20")

            elif key == keyboard.Key.space:
                print("SPACE pressed - Emergency stop")
                self.tello.send_command("emergency")

            elif key == keyboard.Key.esc:
                print("ESC pressed - Exiting program...")
                self.is_running = False
                # Stop listener
                return False

        except Exception as e:
            print(f"Error handling key press: {e}")

    def run(self):
        """Main run loop with keyboard listener"""
        try:
            with keyboard.Listener(on_press=self.on_press) as listener:
                while self.is_running:
                    time.sleep(0.1)
                listener.stop()

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
