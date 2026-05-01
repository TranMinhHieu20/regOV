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

def get_hidemium_profiles_map():
    """Gọi API nội bộ của Hidemium để lấy bản đồ {uuid: tên_profile}"""
    mapping = {}
    try:
        resp = requests.post('http://127.0.0.1:2222/v1/browser/list?is_local=false', json={'page':1, 'limit':1000}, timeout=2)
        if resp.status_code == 200:
            data = resp.json()
            if "data" in data and "content" in data["data"]:
                for item in data["data"]["content"]:
                    mapping[item["uuid"]] = item["name"]
    except:
        pass
    return mapping

def get_all_running_hidemium():
    """Tìm tất cả các Hidemium đang chạy và trả về danh sách port và tên profile"""
    uuid_map = get_hidemium_profiles_map()
    
    profiles = []
    for proc in psutil.process_iter(['name', 'cmdline', 'pid']):
        try:
            cmd = proc.info['cmdline']
            if cmd and ('chrome.exe' in proc.info['name'].lower() or 'hidemium' in proc.info['name'].lower()):
                port = None
                profile_dir = f"PID: {proc.info['pid']}"
                for arg in cmd:
                    if '--remote-debugging-port=' in arg:
                        port = arg.split('=')[1]
                    if '--user-data-dir=' in arg:
                        raw_uuid = arg.split('=')[1].split('\\')[-1].split('/')[-1]
                        profile_dir = uuid_map.get(raw_uuid, raw_uuid) # Đổi UUID thành Tên thật
                
                if port:
                    profiles.append({"port": port, "profile": profile_dir})
        except: pass
    
    # Loại bỏ trùng lặp
    unique_profiles = []
    seen_ports = set()
    for p in profiles:
        if p["port"] not in seen_ports:
            unique_profiles.append(p)
            seen_ports.add(p["port"])
            
    return unique_profiles

def get_websocket_url(port):
    """Lấy link WebSocket từ port để Playwright kết nối"""
    try:
        resp = requests.get(f"http://127.0.0.1:{port}/json/version", timeout=3)
        return resp.json()['webSocketDebuggerUrl']
    except: return None