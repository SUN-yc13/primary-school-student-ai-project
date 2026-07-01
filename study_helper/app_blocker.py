"""
应用屏蔽模块
专注时段自动屏蔽指定软件
"""
import time
import threading
import psutil


class AppBlocker:
    """应用屏蔽器"""
    
    def __init__(self, data_manager=None):
        self.data_manager = data_manager
        self._blocking = False
        self._monitor_thread = None
        self._stop_event = threading.Event()
        self._check_interval = 5  # 检查间隔（秒）
        
        # 回调
        self.on_app_blocked = None
    
    def start_blocking(self, app_list=None):
        """开始屏蔽"""
        if self._blocking:
            return
        
        if app_list is None and self.data_manager:
            app_list = self.data_manager.get_enabled_blocklist()
        
        if not app_list:
            return
        
        self._blocking = True
        self._stop_event.clear()
        
        self._monitor_thread = threading.Thread(
            target=self._monitor_apps,
            args=(app_list,),
            daemon=True
        )
        self._monitor_thread.start()
    
    def stop_blocking(self):
        """停止屏蔽"""
        self._blocking = False
        self._stop_event.set()
        
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=2)
    
    def _monitor_apps(self, app_list):
        """监控应用进程"""
        process_names = [app["process_name"].lower() for app in app_list]
        
        while not self._stop_event.is_set():
            try:
                # 遍历所有进程
                for proc in psutil.process_iter(['pid', 'name', 'exe']):
                    try:
                        proc_name = proc.info['name'].lower()
                        
                        # 检查是否在屏蔽列表中
                        if proc_name in process_names:
                            # 终止进程
                            try:
                                proc.terminate()
                                if self.on_app_blocked:
                                    self.on_app_blocked(proc.info['name'])
                            except (psutil.NoSuchProcess, psutil.AccessDenied):
                                pass
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
            except Exception:
                pass
            
            # 等待下一次检查
            self._stop_event.wait(self._check_interval)
    
    def is_blocking(self):
        """是否正在屏蔽"""
        return self._blocking
    
    def get_running_apps(self):
        """获取当前运行的应用列表"""
        apps = []
        seen = set()
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    name = proc.info['name']
                    if name and name.lower() not in seen:
                        seen.add(name.lower())
                        apps.append({
                            'name': name,
                            'pid': proc.info['pid'],
                            'exe': proc.info.get('exe', '')
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception:
            pass
        
        # 按名称排序
        apps.sort(key=lambda x: x['name'].lower())
        return apps
    
    def get_common_distracting_apps(self):
        """获取常见的分心应用列表"""
        return [
            {"app_name": "微信", "process_name": "WeChat.exe"},
            {"app_name": "QQ", "process_name": "QQ.exe"},
            {"app_name": "抖音", "process_name": "douyin.exe"},
            {"app_name": "哔哩哔哩", "process_name": "哔哩哔哩.exe"},
            {"app_name": "微博", "process_name": "weibo.exe"},
            {"app_name": "淘宝", "process_name": "taobao.exe"},
            {"app_name": "网易云音乐", "process_name": "cloudmusic.exe"},
            {"app_name": "QQ音乐", "process_name": "QQMusic.exe"},
            {"app_name": "Steam", "process_name": "steam.exe"},
            {"app_name": "英雄联盟", "process_name": "LeagueClient.exe"},
            {"app_name": "爱奇艺", "process_name": "QyClient.exe"},
            {"app_name": "腾讯视频", "process_name": "QQLive.exe"},
            {"app_name": "优酷", "process_name": "youku.exe"},
            {"app_name": "爱奇艺视频", "process_name": "iQIYI.exe"},
        ]
