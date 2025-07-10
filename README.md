# Automate anything toolkit

A Python-based system for tracking gestures on a master Android device and replicating them across multiple slave devices in real-time. Perfect for testing apps across multiple devices simultaneously or creating synchronized device demonstrations.

## Features

- **Multi-Device Control**: Control multiple Android devices simultaneously
- **Gesture Tracking**: Captures touch gestures (taps, swipes) from a master device
- **Real-Time Replication**: Instantly replicates gestures across all connected slave devices
- **Device Memory**: Remembers previously connected devices for faster reconnection
- **WiFi Connection**: Automatically switches devices from USB to WiFi for wireless operation
- **Smart Reconnection**: Attempts to reconnect to known devices automatically

## Requirements

### Software Dependencies
- Python 3.7+
- ADB (Android Debug Bridge)
- Git (for cloning repository)

### Python Packages
- uiautomator2
- subprocess (built-in)
- threading (built-in)
- time (built-in)
- json (built-in)
- os (built-in)

### Android Device Requirements
- Android devices with USB debugging enabled
- All devices connected to the same WiFi network
- Developer options enabled on all devices

## Installation

1. **Install ADB (Android Debug Bridge):**
   
   **Ubuntu/Debian:**
   ```bash
   sudo apt update
   sudo apt install android-tools-adb
   ```
   
   **Windows:**
   - Download Android SDK Platform Tools from Google
   - Add to system PATH
   
   **macOS:**
   ```bash
   brew install android-platform-tools
   ```

2. **Clone or download the project files**

3. **Set up Python virtual environment (recommended):**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   
   # Activate virtual environment
   # On Linux/macOS:
   source venv/bin/activate
   # On Windows:
   venv\Scripts\activate
   ```

4. **Install Python dependencies:**
   ```bash
   pip install uiautomator2
   ```

5. **Create requirements.txt (optional but recommended):**
   ```bash
   pip freeze > requirements.txt
   ```

6. **Verify ADB installation:**
   ```bash
   adb version
   ```

## Project Structure

```
├── main.py              # Core device management and WiFi switching
├── device_map.py        # Device mapping and reconnection logic
├── gesture_tracker.py   # Gesture detection and replication
├── run.py              # Main entry point
├── device_map.json     # Auto-generated device mapping file
├── requirements.txt    # Python dependencies (optional)
└── venv/              # Virtual environment directory (recommended)
```

## Quick Start

1. **Create and activate virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or
   venv\Scripts\activate     # Windows
   ```

2. **Install dependencies:**
   ```bash
   pip install uiautomator2
   ```

3. **Connect Android devices via USB**

4. **Run the program:**
   ```bash
   python3 run.py
   ```

## Usage

### Initial Setup

1. **Enable Developer Options** on all Android devices:
   - Go to Settings > About Phone
   - Tap "Build Number" 7 times
   - Go back to Settings > Developer Options
   - Enable "USB Debugging"

2. **Connect devices via USB** to your computer

3. **Ensure all devices are on the same WiFi network**

### Running the Program

**Make sure your virtual environment is activated:**
```bash
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows
```

**Run the main program:**
```bash
python3 run.py
```

**To deactivate virtual environment when done:**
```bash
deactivate
```

### First Run Workflow

1. **Device Discovery**: Program detects all USB-connected devices
2. **WiFi Switching**: Automatically switches devices to WiFi connection
3. **Device Selection**: Choose which device will be the master
4. **Gesture Tracking**: Start performing gestures on the master device
5. **Real-Time Replication**: Watch gestures replicate on all slave devices

### Subsequent Runs

- Program automatically attempts to reconnect to previously known devices
- Only new devices need to go through the WiFi switching process
- Faster startup due to device memory

## How It Works

### Device Connection Flow
1. **USB Detection**: Discovers devices connected via USB
2. **IP Resolution**: Determines each device's WiFi IP address
3. **TCP Mode**: Switches devices to TCP mode on port 5555
4. **WiFi Connection**: Connects to devices wirelessly
5. **Device Mapping**: Saves device information for future reconnection

### Gesture Tracking
1. **Touch Event Monitoring**: Listens to `/dev/input/event4` on master device
2. **Coordinate Processing**: Converts raw touch coordinates to screen pixels
3. **Gesture Detection**: Identifies taps, swipes, and directional movements
4. **Command Generation**: Creates uiautomator2 commands for each gesture
5. **Multi-Threading**: Executes commands simultaneously across all slave devices

## Configuration

### Screen Resolution
Default screen resolution is set to 720x1600. Modify in `run.py`:
```python
MAX_X, MAX_Y = 720, 1600
SCREEN_X, SCREEN_Y = 720, 1600
```

### Touch Input Device
Default touch input device is `/dev/input/event4`. Change in `run.py` if needed:
```python
["adb", "-s", master_id, "shell", "getevent", "-lt", "/dev/input/event4"]
```

### Gesture Sensitivity
Adjust swipe detection threshold in `run.py`:
```python
def detect_swipe(start, end, threshold=50):
```

## Troubleshooting

### Common Issues

**"No devices available"**
- Ensure devices are connected via USB
- Check that USB debugging is enabled
- Verify ADB can see devices: `adb devices`

**"Connection refused" errors**
- Ensure all devices are on the same WiFi network
- Check that devices haven't changed IP addresses
- Try restarting the program to refresh connections

**"Could not determine IP" errors**
- Verify devices are connected to WiFi
- Check that the WiFi interface is named `wlan0`
- Some devices may use different network interface names

**Gestures not replicating**
- Ensure all slave devices are unlocked
- Check that uiautomator2 is properly installed on devices
- Verify screen coordinates match your device resolution

### Debug Commands

**Check connected devices:**
```bash
adb devices
```

**Check device IP:**
```bash
adb -s <device_id> shell ip route get 1
```

**Test uiautomator2 connection:**
```bash
python3 -c "import uiautomator2 as u2; d = u2.connect('IP:5555'); print(d.info)"
```

## Device Mapping

The program creates a `device_map.json` file to remember device information:

```json
{
  "SM-A042F_R9ZW302DAHW": {
    "usb_id": "R9ZW302DAHW",
    "wifi_id": "10.94.22.54:5555",
    "model": "SM-A042F",
    "serial": "R9ZW302DAHW"
  }
}
```

This enables faster reconnection on subsequent runs.

## Performance Tips

### For Future Installations

If you want to recreate the environment on another machine:

1. **Create requirements.txt:**
   ```bash
   # With virtual environment activated
   pip freeze > requirements.txt
   ```

2. **On new machine:**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install from requirements
   pip install -r requirements.txt
   ```

### Virtual Environment Benefits

- **Isolation**: Prevents conflicts with system Python packages
- **Reproducibility**: Easy to recreate exact environment
- **Clean Management**: Simple to remove by deleting venv folder
- **Version Control**: Can be excluded from git with `.gitignore`

### Recommended .gitignore

```
# Virtual Environment
venv/
.venv/

# Device mapping (optional - contains device-specific data)
device_map.json

# Python cache
__pycache__/
*.pyc
*.pyo
*.pyd

# IDE files
.vscode/
.idea/
*.swp
*.swo
```

- **WiFi Network**: Use a stable, high-speed WiFi network
- **Device Placement**: Keep devices close to the WiFi router
- **Background Apps**: Close unnecessary apps on all devices
- **Screen On**: Keep all device screens active during operation

## Limitations

- Requires all devices to be on the same WiFi network
- Limited to Android devices with USB debugging enabled
- Gesture detection is specific to the input device path
- Screen coordinates may need adjustment for different resolutions

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is provided as-is for educational and testing purposes.