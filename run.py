import subprocess, time
from main import get_usb_devices, switch_to_wifi, choose_master, setup_sessions

MAX_X, MAX_Y = 720, 1600
SCREEN_X, SCREEN_Y = 720, 1600

def convert_raw_to_pixels(x_raw, y_raw):
    x = int((x_raw / MAX_X) * SCREEN_X)
    y = int((y_raw / MAX_Y) * SCREEN_Y)
    return x, y

def detect_swipe(start, end, threshold=50):
    dx, dy = end[0] - start[0], end[1] - start[1]
    distance = (dx**2 + dy**2)**0.5
    if distance < threshold:
        return "Tap", f"d.click({start[0]}, {start[1]})"
    direction = "→ Right" if dx > 0 else "← Left" if abs(dx) > abs(dy) else "↓ Down" if dy > 0 else "↑ Up"
    return direction, f"d.swipe({start[0]}, {start[1]}, {end[0]}, {end[1]}, duration=0.2)"

def execute_on_device(d, command):
    try: exec(command)
    except Exception as e: print(f"❌ Error on {d.serial}: {e}")

def execute_command(command, sessions):
    import threading
    threads = [threading.Thread(target=execute_on_device, args=(d, command)) for d in sessions.values()]
    for t in threads: t.start()
    for t in threads: t.join()

def track_gesture(master_id, sessions):
    print(f"📲 Tracking gestures on master: {master_id}")
    proc = subprocess.Popen(
        ["adb", "-s", master_id, "shell", "getevent", "-lt", "/dev/input/event4"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    tracking = False
    current_x = current_y = None
    start_point = None
    touch_start_time = None
    points = []
    
    try:
        for line in proc.stdout:
            if "ABS_MT_TRACKING_ID" in line:
                if "ffffffff" in line:
                    if tracking and start_point:
                        end_point = points[-1] if points else start_point
                        gesture, command = detect_swipe(start_point, end_point)
                        duration = time.time() - touch_start_time
                        # print(f"👆 Gesture → {gesture} | {command} | Duration: {duration:.2f}s")
                        execute_command(command, sessions)
                    tracking = False
                    points.clear()
                    start_point = touch_start_time = None
                else:
                    tracking = True
                    points.clear()
                    start_point = None
                    touch_start_time = time.time()
            elif tracking and "ABS_MT_POSITION_X" in line:
                raw_x = int(line.strip().split()[-1], 16)
                current_x, _ = convert_raw_to_pixels(raw_x, 0)
            elif tracking and "ABS_MT_POSITION_Y" in line:
                raw_y = int(line.strip().split()[-1], 16)
                _, current_y = convert_raw_to_pixels(0, raw_y)
            elif tracking and "SYN_REPORT" in line and current_x and current_y:
                point = (current_x, current_y)
                points.append(point)
                if start_point is None:
                    start_point = point
                current_x = current_y = None
    except KeyboardInterrupt:
        proc.terminate()
        print("\n🛑 Listener stopped.")

if __name__ == "__main__":
    usb_ids = get_usb_devices()
    wifi_ids = switch_to_wifi(usb_ids)
    master_id, slave_ids = choose_master(wifi_ids)
    sessions = setup_sessions(slave_ids)
    track_gesture(master_id, sessions)