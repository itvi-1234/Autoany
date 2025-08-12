import subprocess
import time
import uiautomator2 as u2
from device_map import (
    load_device_map, save_device_map, update_device_map, 
    get_known_devices, try_reconnect_known_devices
)

def get_usb_devices():
    output = subprocess.run(["adb", "devices"], capture_output=True, text=True).stdout
    lines = output.strip().splitlines()[1:]
    return [line.split()[0] for line in lines if "device" in line]

def get_wifi_ip(device):
    # Try multiple methods to get device IP
    methods = [
        ["adb", "-s", device, "shell", "ip", "route", "get", "1"],
        ["adb", "-s", device, "shell", "ip", "addr", "show", "wlan0"],
        ["adb", "-s", device, "shell", "ifconfig", "wlan0"],
        ["adb", "-s", device, "shell", "ip", "route"]
    ]
    
    for method in methods:
        try:
            result = subprocess.run(method, capture_output=True, text=True).stdout
            
            # Method 1: ip route get 1
            if "src" in result and len(result.split("src")) > 1:
                ip_part = result.split("src")[1].strip().split()[0]
                if ip_part and "." in ip_part:
                    return ip_part
            
            # Method 2: ip addr show wlan0
            if "inet " in result:
                for line in result.split('\n'):
                    if "inet " in line:
                        ip_part = line.strip().split()[1].split('/')[0]
                        if ip_part and "." in ip_part:
                            return ip_part
            
            # Method 3: ifconfig wlan0
            if "inet addr:" in result:
                ip_part = result.split("inet addr:")[1].split()[0]
                if ip_part and "." in ip_part:
                    return ip_part
                    
        except Exception as e:
            continue
    
    # Fallback: get IP from ADB connection info
    try:
        result = subprocess.run(["adb", "-s", device, "shell", "getprop", "dhcp.wlan0.ipaddress"], 
                            capture_output=True, text=True).stdout.strip()
        if result and "." in result:
            return result
    except:
        pass
    
    raise Exception(f"Could not determine IP for device {device}")

def switch_to_wifi(devices):
    device_map = load_device_map()
    wifi_ids = []
    
    # First, try to reconnect to known devices
    print("🔄 Attempting to reconnect to known devices...")
    reconnected_devices = try_reconnect_known_devices(device_map)
    wifi_ids.extend(reconnected_devices)
    
    # Process new USB devices
    for dev in devices:
        try:
            ip = get_wifi_ip(dev)
            wifi_id = f"{ip}:5555"
            
            # Skip if already in wifi_ids (from reconnection or previous processing)
            if wifi_id in wifi_ids:
                print(f"📱 {dev} already connected via WiFi as {wifi_id}")
                continue
                
            print(f"🔄 Switching {dev} to WiFi at {ip}...")
            
            # Enable TCP mode
            tcp_result = subprocess.run(["adb", "-s", dev, "tcpip", "5555"], 
                                    capture_output=True, text=True)
            if tcp_result.returncode != 0:
                print(f"❌ Failed to enable TCP mode on {dev}")
                continue
            
            # Wait a moment for TCP mode to initialize
            time.sleep(2)
            
            # Connect via WiFi
            connect_result = subprocess.run(["adb", "connect", wifi_id], 
                                          capture_output=True, text=True)
            
            if "connected" in connect_result.stdout.lower() or "already connected" in connect_result.stdout.lower():
                print(f"✅ Connected to {dev} via WiFi at {wifi_id}")
                wifi_ids.append(wifi_id)
                # Update device map with new connection
                device_map = update_device_map(device_map, dev, wifi_id)
            else:
                print(f"❌ Failed to connect to {dev} via WiFi: {connect_result.stdout.strip()}")
                # Still add to wifi_ids if we got this far, connection might work
                wifi_ids.append(wifi_id)
                device_map = update_device_map(device_map, dev, wifi_id)
                
        except Exception as e:
            print(f"❌ Error processing device {dev}: {e}")
            continue
    
    # Remove duplicates while preserving order
    unique_wifi_ids = []
    seen = set()
    for wifi_id in wifi_ids:
        if wifi_id not in seen:
            unique_wifi_ids.append(wifi_id)
            seen.add(wifi_id)
    
    # Save updated device map
    save_device_map(device_map)
    
    return unique_wifi_ids

def choose_master(wifi_ids):
    if not wifi_ids:
        print("❌ No devices available. Exiting...")
        exit(1)
        
    device_map = load_device_map()
    
    print("\n📱 Available Devices:")
    for i, dev in enumerate(wifi_ids):
        # Try to find device info from map
        device_info = "Unknown Device"
        for key, info in device_map.items():
            if info["wifi_id"] == dev:
                device_info = f"{info['model']} ({info['serial']})"
                break
        
        print(f"{i} → {dev} - {device_info}")
    
    index = int(input("Select master device: "))
    return wifi_ids[index], [dev for i, dev in enumerate(wifi_ids) if i != index]

def setup_sessions(slaves):
    return {dev: u2.connect(dev) for dev in slaves}
