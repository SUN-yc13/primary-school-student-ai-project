"""
数据管理模块
使用JSON文件本地持久化用户数据
"""
import os
import json
from pathlib import Path
from datetime import datetime, date


class DataManager:
    """数据管理器"""
    
    def __init__(self, data_dir=None):
        if data_dir:
            self.data_dir = Path(data_dir)
        else:
            # 默认保存在用户目录下
            self.data_dir = Path.home() / ".study_helper"
        
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 数据文件路径
        self.todo_file = self.data_dir / "todos.json"
        self.stats_file = self.data_dir / "statistics.json"
        self.settings_file = self.data_dir / "settings.json"
        self.notes_file = self.data_dir / "notes.json"
        self.blocklist_file = self.data_dir / "blocklist.json"
        
        # 初始化数据文件
        self._init_files()
    
    def _init_files(self):
        """初始化数据文件"""
        # 待办清单
        if not self.todo_file.exists():
            self._save_json(self.todo_file, {"todos": []})
        
        # 统计数据
        if not self.stats_file.exists():
            self._save_json(self.stats_file, {"daily": {}, "total": {"focus_minutes": 0, "sessions": 0}})
        
        # 设置
        if not self.settings_file.exists():
            default_settings = {
                "pomodoro_duration": 25,  # 分钟
                "short_break": 5,
                "long_break": 15,
                "long_break_interval": 4,
                "auto_start_break": True,
                "auto_start_pomodoro": False,
                "sound_enabled": True,
                "notification_enabled": True
            }
            self._save_json(self.settings_file, default_settings)
        
        # 便签
        if not self.notes_file.exists():
            self._save_json(self.notes_file, {"notes": []})
        
        # 屏蔽列表
        if not self.blocklist_file.exists():
            self._save_json(self.blocklist_file, {"apps": []})
    
    def _load_json(self, file_path):
        """加载JSON文件"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _save_json(self, file_path, data):
        """保存JSON文件"""
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    # ========== 待办清单相关 ==========
    def get_todos(self):
        """获取所有待办事项"""
        data = self._load_json(self.todo_file)
        return data.get("todos", [])
    
    def add_todo(self, text, priority="medium", due_date=None):
        """添加待办事项"""
        todos = self.get_todos()
        new_todo = {
            "id": int(datetime.now().timestamp() * 1000),
            "text": text,
            "completed": False,
            "priority": priority,
            "due_date": due_date,
            "created_at": datetime.now().isoformat(),
            "completed_at": None
        }
        todos.append(new_todo)
        self._save_json(self.todo_file, {"todos": todos})
        return new_todo
    
    def update_todo(self, todo_id, **kwargs):
        """更新待办事项"""
        todos = self.get_todos()
        for todo in todos:
            if todo["id"] == todo_id:
                todo.update(kwargs)
                if kwargs.get("completed") and not todo.get("completed_at"):
                    todo["completed_at"] = datetime.now().isoformat()
                break
        self._save_json(self.todo_file, {"todos": todos})
    
    def delete_todo(self, todo_id):
        """删除待办事项"""
        todos = self.get_todos()
        todos = [t for t in todos if t["id"] != todo_id]
        self._save_json(self.todo_file, {"todos": todos})
    
    def clear_completed(self):
        """清除已完成的待办"""
        todos = self.get_todos()
        todos = [t for t in todos if not t["completed"]]
        self._save_json(self.todo_file, {"todos": todos})
    
    # ========== 统计相关 ==========
    def add_focus_session(self, minutes, date_str=None):
        """添加专注记录"""
        if date_str is None:
            date_str = date.today().isoformat()
        
        stats = self._load_json(self.stats_file)
        
        # 更新每日统计
        if date_str not in stats["daily"]:
            stats["daily"][date_str] = {"focus_minutes": 0, "sessions": 0}
        
        stats["daily"][date_str]["focus_minutes"] += minutes
        stats["daily"][date_str]["sessions"] += 1
        
        # 更新总计
        stats["total"]["focus_minutes"] += minutes
        stats["total"]["sessions"] += 1
        
        self._save_json(self.stats_file, stats)
    
    def get_daily_stats(self, date_str=None):
        """获取某日统计"""
        if date_str is None:
            date_str = date.today().isoformat()
        
        stats = self._load_json(self.stats_file)
        return stats["daily"].get(date_str, {"focus_minutes": 0, "sessions": 0})
    
    def get_weekly_stats(self):
        """获取最近7天统计"""
        from datetime import timedelta
        stats = self._load_json(self.stats_file)
        weekly = []
        
        for i in range(6, -1, -1):
            d = date.today() - timedelta(days=i)
            date_str = d.isoformat()
            day_data = stats["daily"].get(date_str, {"focus_minutes": 0, "sessions": 0})
            weekly.append({
                "date": date_str,
                "weekday": d.strftime("%A"),
                "weekday_cn": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][d.weekday()],
                "focus_minutes": day_data["focus_minutes"],
                "sessions": day_data["sessions"]
            })
        
        return weekly
    
    def get_total_stats(self):
        """获取总统计"""
        stats = self._load_json(self.stats_file)
        return stats.get("total", {"focus_minutes": 0, "sessions": 0})
    
    # ========== 设置相关 ==========
    def get_settings(self):
        """获取设置"""
        return self._load_json(self.settings_file)
    
    def update_settings(self, **kwargs):
        """更新设置"""
        settings = self.get_settings()
        settings.update(kwargs)
        self._save_json(self.settings_file, settings)
    
    # ========== 便签相关 ==========
    def get_notes(self):
        """获取所有便签"""
        data = self._load_json(self.notes_file)
        return data.get("notes", [])
    
    def add_note(self, content, x=100, y=100, width=250, height=200):
        """添加便签"""
        notes = self.get_notes()
        new_note = {
            "id": int(datetime.now().timestamp() * 1000),
            "content": content,
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "color": "yellow",
            "created_at": datetime.now().isoformat()
        }
        notes.append(new_note)
        self._save_json(self.notes_file, {"notes": notes})
        return new_note
    
    def update_note(self, note_id, **kwargs):
        """更新便签"""
        notes = self.get_notes()
        for note in notes:
            if note["id"] == note_id:
                note.update(kwargs)
                break
        self._save_json(self.notes_file, {"notes": notes})
    
    def delete_note(self, note_id):
        """删除便签"""
        notes = self.get_notes()
        notes = [n for n in notes if n["id"] != note_id]
        self._save_json(self.notes_file, {"notes": notes})
    
    # ========== 屏蔽列表相关 ==========
    def get_blocklist(self):
        """获取屏蔽应用列表"""
        data = self._load_json(self.blocklist_file)
        return data.get("apps", [])
    
    def add_to_blocklist(self, app_name, process_name):
        """添加应用到屏蔽列表"""
        apps = self.get_blocklist()
        # 检查是否已存在
        for app in apps:
            if app["process_name"].lower() == process_name.lower():
                return False
        
        new_app = {
            "id": int(datetime.now().timestamp() * 1000),
            "app_name": app_name,
            "process_name": process_name,
            "enabled": True,
            "created_at": datetime.now().isoformat()
        }
        apps.append(new_app)
        self._save_json(self.blocklist_file, {"apps": apps})
        return True
    
    def remove_from_blocklist(self, app_id):
        """从屏蔽列表移除"""
        apps = self.get_blocklist()
        apps = [a for a in apps if a["id"] != app_id]
        self._save_json(self.blocklist_file, {"apps": apps})
    
    def toggle_blocklist_app(self, app_id, enabled):
        """切换屏蔽应用启用状态"""
        apps = self.get_blocklist()
        for app in apps:
            if app["id"] == app_id:
                app["enabled"] = enabled
                break
        self._save_json(self.blocklist_file, {"apps": apps})
    
    def get_enabled_blocklist(self):
        """获取已启用的屏蔽列表"""
        apps = self.get_blocklist()
        return [a for a in apps if a["enabled"]]
