import psutil
import requests

def find_hidemium_debug_port():
    """Tìm port debugging của Hidemium từ các tiến trình đang chạy"""
    for proc in psutil.process_iter(['name', 'cmdline']):
        try:
            cmd = proc.info['cmdline']
            if cmd and ('chrome.exe' in proc.info['name'].lower() or 'hidemium' in proc.info['name'].lower()):
                for arg in cmd:
                    if '--remote-debugging-port=' in arg:
                        return arg.split('=')[1]
        except: pass
    return None

def get_websocket_url(port):
    """Lấy link WebSocket từ port để Playwright kết nối"""
    try:
        resp = requests.get(f"http://127.0.0.1:{port}/json/version", timeout=3)
        return resp.json()['webSocketDebuggerUrl']
    except: return None