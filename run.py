import subprocess, time
from main import get_usb_devices, switch_to_wifi, choose_master, setup_sessions

MAX_X, MAX_Y = 720, 1600
SCREEN_X, SCREEN_Y = 720, 1600

def convert_raw_to_pixels(x_raw, y_raw):
    x = int((x_raw / MAX_X) * SCREEN_X)
    y = int((y_raw / MAX_Y) * SCREEN_Y)
    return x, y

def detect_swipe(start, end, threshold=50):
    
    print("detect_swipe code available upon request to prevent unauthorized cloning.")

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
   
    print("track_gesture code available upon request to prevent unauthorized cloning.")

if __name__ == "__main__":
    usb_ids = get_usb_devices()
    wifi_ids = switch_to_wifi(usb_ids)
    master_id, slave_ids = choose_master(wifi_ids)
    sessions = setup_sessions(slave_ids)
    track_gesture(master_id, sessions)