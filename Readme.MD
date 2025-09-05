# Tello Drone Pilot

## Keyboard Controls

| Key         | Action                        |
|-------------|------------------------------|
| ENTER       | Takeoff                       |
| DEL         | Land                          |
| UP Arrow    | Move up 20cm (hold for repeat)|
| DOWN Arrow  | Move down 20cm (hold for repeat)|
| LEFT Arrow  | Move left 20cm (hold for repeat)|
| RIGHT Arrow | Move right 20cm (hold for repeat)|
| W           | Move forward 20cm (hold for repeat)|
| S           | Move back 20cm (hold for repeat)|
| SPACE       | Emergency stop                |
| ESC         | Exit                          |

- **Hold movement keys** for continuous movement (every 0.15s).
- The drone must be airborne (after takeoff) to accept movement commands.
- Minimum safe move distance is 20cm.
- Flight logs are saved automatically in the `log/` directory after each session.

## GUI Controls

A modern GUI is available using `customtkinter`:

- **Takeoff** and **Land** buttons
- **Directional movement** (Up, Down, Left, Right, Forward, Back) — *hold buttons for continuous movement*
- **Emergency** button for immediate stop
- **Live stats**: Battery, Speed, Altitude (auto-updating)
- **Dark mode** interface

To run the GUI:
```bash
python gui_controller.py
```

## Acceptable Tello Drone SDK Commands

Below is a list of common commands supported by the Tello drone (per the Tello SDK 1.3):

### Basic Flight Commands

- `command` — Enter SDK mode
- `takeoff` — Auto takeoff
- `land` — Auto landing
- `emergency` — Stop all motors immediately

### Movement (distance in cm, 20–500)

- `up x` — Move up x cm
- `down x` — Move down x cm
- `left x` — Move left x cm
- `right x` — Move right x cm
- `forward x` — Move forward x cm
- `back x` — Move back x cm

### Rotation

- `cw x` — Rotate clockwise x degrees (1–3600)
- `ccw x` — Rotate counter-clockwise x degrees (1–3600)

### Flip

- `flip l` — Flip left
- `flip r` — Flip right
- `flip f` — Flip forward
- `flip b` — Flip back

### Speed

- `speed x` — Set speed to x cm/s (10–100)
- `speed?` — Query current speed

### Status Queries

- `battery?` — Query battery percentage
- `time?` — Query flight time
- `height?` — Query height
- `temp?` — Query temperature
- `attitude?` — Query pitch/roll/yaw
- `baro?` — Query barometer value
- `acceleration?` — Query acceleration
- `tof?` — Query TOF distance

### Stream

- `streamon` — Enable video stream
- `streamoff` — Disable video stream

---

For more details, see the official Tello SDK documentation.
https://github.com/dji-sdk/Tello-Python

