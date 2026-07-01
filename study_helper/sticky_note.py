"""
置顶便签模块
可置顶的桌面便签
"""
import tkinter as tk
from tkinter import ttk, messagebox


class StickyNote:
    """置顶便签窗口"""
    
    COLORS = {
        "yellow": "#FFF9C4",
        "green": "#C8E6C9",
        "blue": "#BBDEFB",
        "pink": "#F8BBD0",
        "orange": "#FFE0B2",
        "purple": "#E1BEE7"
    }
    
    def __init__(self, master, note_data, data_manager, on_close=None):
        self.master = master
        self.note_data = note_data
        self.data_manager = data_manager
        self.on_close = on_close
        
        # 创建顶层窗口
        self.window = tk.Toplevel(master)
        self.window.title("便签")
        self.window.attributes("-topmost", True)
        
        # 设置位置和大小
        x = note_data.get("x", 100)
        y = note_data.get("y", 100)
        width = note_data.get("width", 250)
        height = note_data.get("height", 200)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
        self.window.minsize(150, 100)
        
        # 移除窗口边框
        self.window.overrideredirect(True)
        
        # 设置背景色
        color_name = note_data.get("color", "yellow")
        self.bg_color = self.COLORS.get(color_name, self.COLORS["yellow"])
        self.window.configure(bg=self.bg_color)
        
        # 创建界面
        self._create_widgets()
        
        # 绑定事件
        self._bind_events()
        
        # 保存位置变化
        self.window.bind("<Configure>", self._on_configure)
    
    def _create_widgets(self):
        """创建界面组件"""
        # 标题栏
        self.title_bar = tk.Frame(self.window, bg=self.bg_color, height=25)
        self.title_bar.pack(fill=tk.X)
        self.title_bar.pack_propagate(False)
        
        # 关闭按钮
        close_btn = tk.Label(
            self.title_bar,
            text="×",
            bg=self.bg_color,
            fg="#666",
            font=("Arial", 12, "bold"),
            cursor="hand2"
        )
        close_btn.pack(side=tk.RIGHT, padx=5)
        close_btn.bind("<Button-1>", self._on_close)
        
        # 最小化按钮
        min_btn = tk.Label(
            self.title_bar,
            text="—",
            bg=self.bg_color,
            fg="#666",
            font=("Arial", 10, "bold"),
            cursor="hand2"
        )
        min_btn.pack(side=tk.RIGHT, padx=5)
        min_btn.bind("<Button-1>", self._on_minimize)
        
        # 颜色切换按钮
        color_btn = tk.Label(
            self.title_bar,
            text="●",
            bg=self.bg_color,
            fg="#999",
            font=("Arial", 8),
            cursor="hand2"
        )
        color_btn.pack(side=tk.LEFT, padx=5)
        color_btn.bind("<Button-1>", self._show_color_menu)
        
        # 内容区域
        self.text_widget = tk.Text(
            self.window,
            wrap=tk.WORD,
            bg=self.bg_color,
            fg="#333",
            font=("Microsoft YaHei", 10),
            bd=0,
            highlightthickness=0,
            padx=10,
            pady=5
        )
        self.text_widget.pack(fill=tk.BOTH, expand=True)
        
        # 插入内容
        content = self.note_data.get("content", "")
        self.text_widget.insert("1.0", content)
        
        # 绑定内容变化事件（延迟保存）
        self.text_widget.bind("<KeyRelease>", self._on_text_changed)
        self._save_timer = None
    
    def _bind_events(self):
        """绑定拖拽事件"""
        self.title_bar.bind("<ButtonPress-1>", self._start_move)
        self.title_bar.bind("<B1-Motion>", self._on_move)
    
    def _start_move(self, event):
        """开始移动窗口"""
        self._drag_x = event.x
        self._drag_y = event.y
    
    def _on_move(self, event):
        """移动窗口"""
        x = self.window.winfo_x() + event.x - self._drag_x
        y = self.window.winfo_y() + event.y - self._drag_y
        self.window.geometry(f"+{x}+{y}")
    
    def _on_configure(self, event):
        """窗口配置变化时保存位置和大小"""
        if hasattr(self, '_save_timer') and self._save_timer:
            self.window.after_cancel(self._save_timer)
        
        self._save_timer = self.window.after(500, self._save_position)
    
    def _save_position(self):
        """保存位置和大小"""
        x = self.window.winfo_x()
        y = self.window.winfo_y()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        
        self.data_manager.update_note(
            self.note_data["id"],
            x=x, y=y, width=width, height=height
        )
    
    def _on_text_changed(self, event):
        """文本变化时延迟保存"""
        if self._save_timer:
            self.window.after_cancel(self._save_timer)
        
        self._save_timer = self.window.after(1000, self._save_content)
    
    def _save_content(self):
        """保存内容"""
        content = self.text_widget.get("1.0", tk.END).strip()
        self.data_manager.update_note(self.note_data["id"], content=content)
    
    def _on_close(self, event):
        """关闭便签"""
        if messagebox.askyesno("确认", "确定要删除这个便签吗？"):
            self._save_content()
            self.data_manager.delete_note(self.note_data["id"])
            self.window.destroy()
            if self.on_close:
                self.on_close(self.note_data["id"])
    
    def _on_minimize(self, event):
        """最小化"""
        self.window.iconify()
    
    def _show_color_menu(self, event):
        """显示颜色菜单"""
        menu = tk.Menu(self.window, tearoff=0)
        
        for color_name, color_hex in self.COLORS.items():
            menu.add_command(
                label="●",
                background=color_hex,
                command=lambda c=color_name: self._change_color(c)
            )
        
        menu.tk_popup(event.x_root, event.y_root)
    
    def _change_color(self, color_name):
        """改变颜色"""
        self.bg_color = self.COLORS.get(color_name, self.COLORS["yellow"])
        self.window.configure(bg=self.bg_color)
        self.title_bar.configure(bg=self.bg_color)
        self.text_widget.configure(bg=self.bg_color)
        
        # 更新标题栏按钮颜色
        for child in self.title_bar.winfo_children():
            child.configure(bg=self.bg_color)
        
        # 保存颜色
        self.data_manager.update_note(self.note_data["id"], color=color_name)
    
    def destroy(self):
        """销毁窗口"""
        if self.window.winfo_exists():
            self.window.destroy()
    
    def show(self):
        """显示窗口"""
        self.window.deiconify()
        self.window.lift()
    
    def hide(self):
        """隐藏窗口"""
        self.window.withdraw()
