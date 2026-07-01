"""
本地化学习效率工具 - 主程序
基于 tkinter 的多标签页界面
"""
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import date, datetime

from data_manager import DataManager
from pomodoro import PomodoroTimer, TimerState
from app_blocker import AppBlocker
from sticky_note import StickyNote


class StudyHelperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("学习效率助手")
        self.root.geometry("850x600")
        self.root.minsize(750, 500)

        self.style = ttk.Style()
        try:
            self.style.theme_use("vista")
        except:
            try:
                self.style.theme_use("clam")
            except:
                pass

        self.data_manager = DataManager()
        self.pomodoro = PomodoroTimer(self.data_manager)
        self.pomodoro.on_tick = self._on_pomodoro_tick
        self.pomodoro.on_state_change = self._on_pomodoro_state_change
        self.pomodoro.on_session_complete = self._on_session_complete
        self.pomodoro.on_break_start = self._on_break_start
        self.pomodoro.on_break_end = self._on_break_end

        self.app_blocker = AppBlocker(self.data_manager)
        self.app_blocker.on_app_blocked = self._on_app_blocked
        self.sticky_notes = {}

        self.create_widgets()
        self._load_existing_notes()
        self._update_stats_display()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        title_label = ttk.Label(main_frame, text="学习效率助手", font=("Microsoft YaHei", 16, "bold"))
        title_label.pack(pady=(0, 10))

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.create_pomodoro_tab()
        self.create_todo_tab()
        self.create_stats_tab()
        self.create_notes_tab()
        self.create_blocker_tab()
        self.create_settings_tab()

        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, pady=(10, 0))

    def create_pomodoro_tab(self):
        tab = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(tab, text="番茄专注")

        container = ttk.Frame(tab)
        container.pack(expand=True)

        self.pomodoro_state_var = tk.StringVar(value="准备开始")
        state_label = ttk.Label(container, textvariable=self.pomodoro_state_var, font=("Microsoft YaHei", 12))
        state_label.pack(pady=(0, 10))

        self.time_var = tk.StringVar(value="25:00")
        time_label = ttk.Label(container, textvariable=self.time_var, font=("Consolas", 64, "bold"))
        time_label.pack(pady=10)

        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(container, variable=self.progress_var, maximum=100, length=300)
        self.progress_bar.pack(pady=10)

        self.pomodoro_count_var = tk.StringVar(value="今日完成: 0 个番茄")
        count_label = ttk.Label(container, textvariable=self.pomodoro_count_var, foreground="#666")
        count_label.pack(pady=(0, 20))

        btn_frame = ttk.Frame(container)
        btn_frame.pack()

        self.start_btn = ttk.Button(btn_frame, text="开始", command=self.start_pomodoro, width=12)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.pause_btn = ttk.Button(btn_frame, text="暂停", command=self.pause_pomodoro, width=12, state=tk.DISABLED)
        self.pause_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(btn_frame, text="停止", command=self.stop_pomodoro, width=12, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        quick_frame = ttk.LabelFrame(tab, text="快捷时长", padding="10")
        quick_frame.pack(fill=tk.X, pady=(20, 0))

        durations = [15, 25, 30, 45, 50, 60]
        for i, mins in enumerate(durations):
            btn = ttk.Button(quick_frame, text=f"{mins}分钟", command=lambda m=mins: self.set_pomodoro_duration(m), width=8)
            btn.grid(row=0, column=i, padx=5, pady=5)

        blocker_frame = ttk.Frame(tab)
        blocker_frame.pack(fill=tk.X, pady=(10, 0))

        self.auto_block_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(blocker_frame, text="专注时自动屏蔽分心应用", variable=self.auto_block_var).pack(side=tk.LEFT)

    def create_todo_tab(self):
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="待办清单")

        add_frame = ttk.Frame(tab)
        add_frame.pack(fill=tk.X, pady=(0, 10))

        self.todo_entry = ttk.Entry(add_frame)
        self.todo_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.todo_entry.bind("<Return>", lambda e: self.add_todo())

        self.todo_priority_var = tk.StringVar(value="medium")
        priority_combo = ttk.Combobox(add_frame, textvariable=self.todo_priority_var, values=["high", "medium", "low"], state="readonly", width=8)
        priority_combo.pack(side=tk.LEFT, padx=5)

        ttk.Button(add_frame, text="添加", command=self.add_todo, width=8).pack(side=tk.LEFT)

        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Button(btn_frame, text="清除已完成", command=self.clear_completed_todos).pack(side=tk.LEFT)

        list_frame = ttk.LabelFrame(tab, text="待办事项", padding="5")
        list_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("priority", "text", "created")
        self.todo_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        self.todo_tree.heading("priority", text="优先级")
        self.todo_tree.heading("text", text="内容")
        self.todo_tree.heading("created", text="创建时间")
        self.todo_tree.column("priority", width=60, anchor=tk.CENTER)
        self.todo_tree.column("text", width=400)
        self.todo_tree.column("created", width=150, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.todo_tree.yview)
        self.todo_tree.configure(yscrollcommand=scrollbar.set)
        self.todo_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.todo_tree.bind("<Double-1>", self.toggle_todo_complete)
        self.todo_tree.bind("<Delete>", self.delete_selected_todo)

        self.todo_menu = tk.Menu(self.root, tearoff=0)
        self.todo_menu.add_command(label="标记完成/未完成", command=self.toggle_todo_complete)
        self.todo_menu.add_command(label="删除", command=self.delete_selected_todo)
        self.todo_tree.bind("<Button-3>", self.show_todo_menu)

        self._load_todos()

    def create_stats_tab(self):
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="学习统计")

        today_frame = ttk.LabelFrame(tab, text="今日统计", padding="15")
        today_frame.pack(fill=tk.X, pady=(0, 10))

        stats_grid = ttk.Frame(today_frame)
        stats_grid.pack()

        self.today_minutes_var = tk.StringVar(value="0")
        ttk.Label(stats_grid, textvariable=self.today_minutes_var, font=("Microsoft YaHei", 24, "bold")).grid(row=0, column=0, padx=20)
        ttk.Label(stats_grid, text="分钟", foreground="#666").grid(row=1, column=0, padx=20)

        self.today_sessions_var = tk.StringVar(value="0")
        ttk.Label(stats_grid, textvariable=self.today_sessions_var, font=("Microsoft YaHei", 24, "bold")).grid(row=0, column=1, padx=20)
        ttk.Label(stats_grid, text="个番茄", foreground="#666").grid(row=1, column=1, padx=20)

        total_frame = ttk.LabelFrame(tab, text="累计统计", padding="15")
        total_frame.pack(fill=tk.X, pady=(0, 10))

        total_grid = ttk.Frame(total_frame)
        total_grid.pack()

        self.total_minutes_var = tk.StringVar(value="0")
        ttk.Label(total_grid, textvariable=self.total_minutes_var, font=("Microsoft YaHei", 24, "bold")).grid(row=0, column=0, padx=20)
        ttk.Label(total_grid, text="总分钟数", foreground="#666").grid(row=1, column=0, padx=20)

        self.total_sessions_var = tk.StringVar(value="0")
        ttk.Label(total_grid, textvariable=self.total_sessions_var, font=("Microsoft YaHei", 24, "bold")).grid(row=0, column=1, padx=20)
        ttk.Label(total_grid, text="总番茄数", foreground="#666").grid(row=1, column=1, padx=20)

        week_frame = ttk.LabelFrame(tab, text="本周统计", padding="10")
        week_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("day", "minutes", "sessions")
        self.week_tree = ttk.Treeview(week_frame, columns=columns, show="headings", height=7)
        self.week_tree.heading("day", text="日期")
        self.week_tree.heading("minutes", text="专注时长(分钟)")
        self.week_tree.heading("sessions", text="番茄数")
        self.week_tree.column("day", width=150, anchor=tk.CENTER)
        self.week_tree.column("minutes", width=150, anchor=tk.CENTER)
        self.week_tree.column("sessions", width=150, anchor=tk.CENTER)
        self.week_tree.pack(fill=tk.BOTH, expand=True)

        ttk.Button(tab, text="刷新统计", command=self._update_stats_display).pack(pady=10)

    def create_notes_tab(self):
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="置顶便签")

        info_label = ttk.Label(tab, text="便签会始终置顶显示在桌面上，可拖拽移动、调整大小、更换颜色。", foreground="#666")
        info_label.pack(pady=(0, 10))

        btn_frame = ttk.Frame(tab)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="新建便签", command=self.create_new_note, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="显示全部", command=self.show_all_notes, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="隐藏全部", command=self.hide_all_notes, width=15).pack(side=tk.LEFT, padx=5)

        list_frame = ttk.LabelFrame(tab, text="便签列表", padding="5")
        list_frame.pack(fill=tk.BOTH, expand=True)

        self.notes_listbox = tk.Listbox(list_frame, font=("Microsoft YaHei", 10))
        self.notes_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self._refresh_notes_list()

    def create_blocker_tab(self):
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="应用屏蔽")

        info_label = ttk.Label(tab, text="专注时可自动屏蔽以下应用，帮助您保持专注。", foreground="#666")
        info_label.pack(pady=(0, 10))

        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(btn_frame, text="添加应用", command=self.add_block_app).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="添加常见应用", command=self.add_common_apps).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="删除选中", command=self.remove_selected_app).pack(side=tk.LEFT, padx=5)

        list_frame = ttk.LabelFrame(tab, text="屏蔽列表", padding="5")
        list_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("enabled", "app_name", "process_name")
        self.blocker_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        self.blocker_tree.heading("enabled", text="启用")
        self.blocker_tree.heading("app_name", text="应用名称")
        self.blocker_tree.heading("process_name", text="进程名")
        self.blocker_tree.column("enabled", width=60, anchor=tk.CENTER)
        self.blocker_tree.column("app_name", width=200)
        self.blocker_tree.column("process_name", width=200)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.blocker_tree.yview)
        self.blocker_tree.configure(yscrollcommand=scrollbar.set)
        self.blocker_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.blocker_tree.bind("<Double-1>", self.toggle_block_app)
        self._load_blocklist()

    def create_settings_tab(self):
        tab = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(tab, text="设置")

        pomo_frame = ttk.LabelFrame(tab, text="番茄钟设置", padding="15")
        pomo_frame.pack(fill=tk.X, pady=(0, 15))

        settings = self.data_manager.get_settings()

        row = 0
        ttk.Label(pomo_frame, text="专注时长(分钟):").grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.focus_duration_var = tk.StringVar(value=str(settings.get("pomodoro_duration", 25)))
        ttk.Entry(pomo_frame, textvariable=self.focus_duration_var, width=10).grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1

        ttk.Label(pomo_frame, text="短休息(分钟):").grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.short_break_var = tk.StringVar(value=str(settings.get("short_break", 5)))
        ttk.Entry(pomo_frame, textvariable=self.short_break_var, width=10).grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1

        ttk.Label(pomo_frame, text="长休息(分钟):").grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.long_break_var = tk.StringVar(value=str(settings.get("long_break", 15)))
        ttk.Entry(pomo_frame, textvariable=self.long_break_var, width=10).grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1

        ttk.Label(pomo_frame, text="长休息间隔(番茄数):").grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        self.long_break_interval_var = tk.StringVar(value=str(settings.get("long_break_interval", 4)))
        ttk.Entry(pomo_frame, textvariable=self.long_break_interval_var, width=10).grid(row=row, column=1, sticky=tk.W, pady=5, padx=5)
        row += 1

        ttk.Button(pomo_frame, text="保存设置", command=self.save_settings).grid(row=row, column=0, columnspan=2, pady=10)

        data_frame = ttk.LabelFrame(tab, text="数据管理", padding="15")
        data_frame.pack(fill=tk.X)

        ttk.Label(data_frame, text=f"数据存储位置: {self.data_manager.data_dir}", foreground="#666").pack(anchor=tk.W, pady=5)
        ttk.Button(data_frame, text="打开数据文件夹", command=self.open_data_folder).pack(anchor=tk.W, pady=5)

    def start_pomodoro(self):
        if self.pomodoro.state == TimerState.PAUSED:
            self.pomodoro.resume()
        else:
            self.pomodoro.start()
        if self.auto_block_var.get():
            self.app_blocker.start_blocking()

    def pause_pomodoro(self):
        self.pomodoro.pause()
        if self.auto_block_var.get():
            self.app_blocker.stop_blocking()

    def stop_pomodoro(self):
        self.pomodoro.stop()
        self.app_blocker.stop_blocking()

    def set_pomodoro_duration(self, minutes):
        self.pomodoro.set_duration(focus_minutes=minutes)
        self.time_var.set(f"{minutes:02d}:00")
        self.progress_var.set(0)

    def _on_pomodoro_tick(self, remaining):
        minutes = remaining // 60
        seconds = remaining % 60
        self.time_var.set(f"{minutes:02d}:{seconds:02d}")
        progress = self.pomodoro.get_progress() * 100
        self.progress_var.set(progress)

    def _on_pomodoro_state_change(self, state):
        state_text = self.pomodoro.get_state_text()
        self.pomodoro_state_var.set(state_text)
        if state == TimerState.RUNNING:
            self.start_btn.config(state=tk.DISABLED)
            self.pause_btn.config(state=tk.NORMAL, text="暂停")
            self.stop_btn.config(state=tk.NORMAL)
        elif state == TimerState.PAUSED:
            self.start_btn.config(state=tk.NORMAL, text="继续")
            self.pause_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
        elif state == TimerState.IDLE:
            self.start_btn.config(state=tk.NORMAL, text="开始")
            self.pause_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.DISABLED)
            self.progress_var.set(0)
        elif state == TimerState.BREAK:
            self.start_btn.config(state=tk.DISABLED)
            self.pause_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)

    def _on_session_complete(self, count):
        messagebox.showinfo("太棒了！", f"完成第 {count} 个番茄！\n休息一下吧~")
        self._update_stats_display()

    def _on_break_start(self, break_type):
        break_text = "长休息" if break_type == "long" else "短休息"
        self.pomodoro_state_var.set(f"{break_text}中")
        self.status_var.set(f"{break_text}开始")

    def _on_break_end(self):
        messagebox.showinfo("休息结束", "休息结束了，准备开始下一个番茄吧！")
        self.status_var.set("休息结束")

    def add_todo(self):
        text = self.todo_entry.get().strip()
        if not text:
            return
        priority = self.todo_priority_var.get()
        self.data_manager.add_todo(text, priority=priority)
        self.todo_entry.delete(0, tk.END)
        self._load_todos()

    def _load_todos(self):
        for item in self.todo_tree.get_children():
            self.todo_tree.delete(item)
        todos = self.data_manager.get_todos()
        priority_order = {"high": 0, "medium": 1, "low": 2}
        todos.sort(key=lambda t: (t["completed"], priority_order.get(t["priority"], 1)))
        for todo in todos:
            priority_text = {"high": "高", "medium": "中", "low": "低"}.get(todo["priority"], "中")
            created = todo.get("created_at", "")
            try:
                dt = datetime.fromisoformat(created)
                created_str = dt.strftime("%m-%d %H:%M")
            except:
                created_str = ""
            item_id = self.todo_tree.insert("", tk.END, values=(priority_text, todo["text"], created_str))
            if todo["completed"]:
                self.todo_tree.item(item_id, tags=("completed",))
        self.todo_tree.tag_configure("completed", foreground="#999")

    def toggle_todo_complete(self, event=None):
        selected = self.todo_tree.selection()
        if not selected:
            return
        item_id = selected[0]
        todos = self.data_manager.get_todos()
        idx = self.todo_tree.index(item_id)
        if idx < len(todos):
            todo = todos[idx]
            self.data_manager.update_todo(todo["id"], completed=not todo["completed"])
            self._load_todos()

    def delete_selected_todo(self, event=None):
        selected = self.todo_tree.selection()
        if not selected:
            return
        if not messagebox.askyesno("确认", "确定要删除选中的待办吗？"):
            return
        item_id = selected[0]
        todos = self.data_manager.get_todos()
        idx = self.todo_tree.index(item_id)
        if idx < len(todos):
            todo = todos[idx]
            self.data_manager.delete_todo(todo["id"])
            self._load_todos()

    def clear_completed_todos(self):
        if not messagebox.askyesno("确认", "确定要清除所有已完成的待办吗？"):
            return
        self.data_manager.clear_completed()
        self._load_todos()

    def show_todo_menu(self, event):
        item = self.todo_tree.identify_row(event.y)
        if item:
            self.todo_tree.selection_set(item)
            self.todo_menu.tk_popup(event.x_root, event.y_root)

    def _update_stats_display(self):
        today_stats = self.data_manager.get_daily_stats()
        self.today_minutes_var.set(str(today_stats["focus_minutes"]))
        self.today_sessions_var.set(str(today_stats["sessions"]))
        self.pomodoro_count_var.set(f"今日完成: {today_stats['sessions']} 个番茄")
        total_stats = self.data_manager.get_total_stats()
        self.total_minutes_var.set(str(total_stats["focus_minutes"]))
        self.total_sessions_var.set(str(total_stats["sessions"]))
        weekly_stats = self.data_manager.get_weekly_stats()
        for item in self.week_tree.get_children():
            self.week_tree.delete(item)
        for day in weekly_stats:
            date_display = f"{day['date']} ({day['weekday_cn']})"
            self.week_tree.insert("", tk.END, values=(date_display, day["focus_minutes"], day["sessions"]))

    def create_new_note(self):
        note = self.data_manager.add_note("", x=150, y=150)
        sticky_note = StickyNote(self.root, note, self.data_manager, on_close=self._on_note_closed)
        self.sticky_notes[note["id"]] = sticky_note
        self._refresh_notes_list()

    def _load_existing_notes(self):
        notes = self.data_manager.get_notes()
        for note in notes:
            sticky_note = StickyNote(self.root, note, self.data_manager, on_close=self._on_note_closed)
            self.sticky_notes[note["id"]] = sticky_note
        self._refresh_notes_list()

    def _on_note_closed(self, note_id):
        if note_id in self.sticky_notes:
            del self.sticky_notes[note_id]
        self._refresh_notes_list()

    def _refresh_notes_list(self):
        self.notes_listbox.delete(0, tk.END)
        notes = self.data_manager.get_notes()
        for note in notes:
            content = note.get("content", "")[:30]
            if len(note.get("content", "")) > 30:
                content += "..."
            self.notes_listbox.insert(tk.END, content or "(空便签)")

    def show_all_notes(self):
        for note in self.sticky_notes.values():
            note.show()

    def hide_all_notes(self):
        for note in self.sticky_notes.values():
            note.hide()

    def _load_blocklist(self):
        for item in self.blocker_tree.get_children():
            self.blocker_tree.delete(item)
        apps = self.data_manager.get_blocklist()
        for app in apps:
            enabled_text = "✓" if app["enabled"] else "✗"
            self.blocker_tree.insert("", tk.END, iid=str(app["id"]), values=(enabled_text, app["app_name"], app["process_name"]))

    def add_block_app(self):
        app_name = simpledialog.askstring("添加应用", "请输入应用名称:")
        if not app_name:
            return
        process_name = simpledialog.askstring("添加应用", "请输入进程名 (如 WeChat.exe):")
        if not process_name:
            return
        if not process_name.endswith(".exe"):
            process_name += ".exe"
        self.data_manager.add_to_blocklist(app_name, process_name)
        self._load_blocklist()

    def add_common_apps(self):
        common_apps = self.app_blocker.get_common_distracting_apps()
        added = 0
        for app in common_apps:
            if self.data_manager.add_to_blocklist(app["app_name"], app["process_name"]):
                added += 1
        self._load_blocklist()
        messagebox.showinfo("完成", f"已添加 {added} 个常见分心应用")

    def remove_selected_app(self):
        selected = self.blocker_tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请选择要删除的应用")
            return
        if not messagebox.askyesno("确认", "确定要删除选中的应用吗？"):
            return
        for item_id in selected:
            app_id = int(item_id)
            self.data_manager.remove_from_blocklist(app_id)
        self._load_blocklist()

    def toggle_block_app(self, event=None):
        selected = self.blocker_tree.selection()
        if not selected:
            return
        item_id = selected[0]
        app_id = int(item_id)
        apps = self.data_manager.get_blocklist()
        for app in apps:
            if app["id"] == app_id:
                self.data_manager.toggle_blocklist_app(app_id, not app["enabled"])
                break
        self._load_blocklist()

    def _on_app_blocked(self, app_name):
        self.status_var.set(f"已屏蔽: {app_name}")

    def save_settings(self):
        try:
            focus_duration = int(self.focus_duration_var.get())
            short_break = int(self.short_break_var.get())
            long_break = int(self.long_break_var.get())
            long_break_interval = int(self.long_break_interval_var.get())
            if focus_duration <= 0 or short_break <= 0 or long_break <= 0 or long_break_interval <= 0:
                raise ValueError("数值必须大于0")
            self.data_manager.update_settings(
                pomodoro_duration=focus_duration,
                short_break=short_break,
                long_break=long_break,
                long_break_interval=long_break_interval
            )
            self.pomodoro.set_duration(focus_minutes=focus_duration, short_break=short_break, long_break=long_break)
            if self.pomodoro.state == TimerState.IDLE:
                self.time_var.set(f"{focus_duration:02d}:00")
            messagebox.showinfo("成功", "设置已保存")
        except ValueError as e:
            messagebox.showerror("错误", f"请输入有效的数字: {e}")

    def open_data_folder(self):
        import subprocess
        try:
            subprocess.run(["explorer", str(self.data_manager.data_dir)])
        except Exception as e:
            messagebox.showerror("错误", f"无法打开文件夹: {e}")


def main():
    root = tk.Tk()
    app = StudyHelperApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
