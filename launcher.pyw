"""
Brasil Fut - Launcher
Opens the game as a standalone app window (no browser chrome).
Requires Python 3.6+ (pre-installed on most Windows systems).
Run with: pythonw launcher.pyw  OR  double-click launcher.pyw
"""
import http.server
import threading
import webbrowser
import subprocess
import sys
import os
import socket
import time

GAME_FILE = "brasil-fut.html"
PORT = 0  # 0 = pick a random available port

def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

def find_browser_path():
    """Find Chrome or Edge executable on Windows."""
    candidates = [
        # Microsoft Edge (pre-installed on Windows 10/11)
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        # Google Chrome
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
        # Chromium
        r"C:\Program Files\Chromium\Application\chromium.exe",
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None

def main():
    # Get absolute path to the game HTML
    script_dir = os.path.dirname(os.path.abspath(__file__))
    game_path = os.path.join(script_dir, GAME_FILE)

    if not os.path.exists(game_path):
        import tkinter.messagebox as mb
        mb.showerror("Brasil Fut", f"Arquivo do jogo não encontrado:\n{game_path}")
        return

    # Start local HTTP server
    port = get_free_port()

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=script_dir, **kwargs)
        def log_message(self, format, *args):
            pass  # suppress console output

    server = http.server.HTTPServer(('127.0.0.1', port), Handler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    url = f"http://127.0.0.1:{port}/{GAME_FILE}"

    # Try to open in app mode (Chrome/Edge --app flag removes browser chrome)
    browser_path = find_browser_path()

    if browser_path:
        # App mode: no address bar, tabs, or browser chrome
        # Creates a proper standalone-looking window
        user_data_dir = os.path.join(os.path.expanduser("~"), ".brasilfut_profile")
        cmd = [
            browser_path,
            f"--app={url}",
            f"--user-data-dir={user_data_dir}",
            "--window-size=1400,900",
            "--no-first-run",
            "--disable-extensions",
        ]
        try:
            process = subprocess.Popen(cmd)
            # Wait for the browser process to close
            process.wait()
        except Exception as e:
            # Fallback: open in default browser
            webbrowser.open(url)
            time.sleep(3)
            input("Press Enter to close the server...")
    else:
        # Fallback: open in default browser (will show browser chrome)
        webbrowser.open(url)
        # Keep server alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass

    # Shutdown server when done
    server.shutdown()

if __name__ == "__main__":
    main()
