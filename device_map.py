import json
import os
import subprocess

DEVICE_MAP_FILE = "device_map.json"

def load_device_map():
    """Load device mapping from file"""
    if os.path.exists(DEVICE_MAP_FILE):
        try:
            with open(DEVICE_MAP_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}

def save_device_map(device_map):
    """Save device mapping to file"""
    try:
        with open(DEVICE_MAP_FILE, 'w') as f:
            json.dump(device_map, f, indent=2)
    except IOError:
        print("⚠️ Warning: Could not save device map")

def get_device_info(device_id):
    """Get device model and serial for mapping"""
    try:
        # Get device model
        model_result = subprocess.run(
            ["adb", "-s", device_id, "shell", "getprop", "ro.product.model"],
            capture_output=True, text=True
        )
        model = model_result.stdout.strip()
        
        # Get device serial
        serial_result = subprocess.run(
            ["adb", "-s", device_id, "shell", "getprop", "ro.serialno"],
            capture_output=True, text=True
        )
        serial = serial_result.stdout.strip()
        
        return {"model": model, "serial": serial}
    except:
        return {"model": "Unknown", "serial": device_id}

def update_device_map(device_map, usb_id, wifi_id):
    """Update device mapping with new USB to WiFi connection"""
    device_info = get_device_info(usb_id)
    device_key = f"{device_info['model']}_{device_info['serial']}"
    
    device_map[device_key] = {
        "usb_id": usb_id,
        "wifi_id": wifi_id,
        "model": device_info['model'],
        "serial": device_info['serial']
    }
    
    return device_map

def get_known_devices(device_map):
    """Get list of known devices that might be reconnectable"""
    known_devices = []
    for key, info in device_map.items():
        known_devices.append({
            "key": key,
            "wifi_id": info["wifi_id"],
            "model": info["model"],
            "serial": info["serial"]
        })
    return known_devices

def try_reconnect_known_devices(device_map):
    """Try to reconnect to previously known devices"""
    reconnected = []
    for key, info in device_map.items():
        wifi_id = info["wifi_id"]
        try:
            # Try to connect to the known WiFi address
            result = subprocess.run(
                ["adb", "connect", wifi_id],
                capture_output=True, text=True
            )
            if "connected" in result.stdout.lower():
                reconnected.append(wifi_id)
                print(f"✅ Reconnected to {info['model']} at {wifi_id}")
            else:
                print(f"❌ Failed to reconnect to {info['model']} at {wifi_id}")
        except:
            print(f"❌ Error reconnecting to {info['model']} at {wifi_id}")
    
    return reconnected
