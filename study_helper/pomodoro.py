"""
番茄专注计时模块
实现番茄工作法计时功能
"""
import time
import threading
from enum import Enum


class TimerState(Enum):
    """计时器状态"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    BREAK = "break"


class PomodoroTimer:
    """番茄钟计时器"""
    
    def __init__(self, data_manager=None):
        self.data_manager = data_manager
        
        # 加载设置
        settings = data_manager.get_settings() if data_manager else {}
        self.focus_duration = settings.get("pomodoro_duration", 25) * 60  # 秒
        self.short_break = settings.get("short_break", 5) * 60
        self.long_break = settings.get("long_break", 15) * 60
        self.long_break_interval = settings.get("long_break_interval", 4)
        
        # 状态
        self.state = TimerState.IDLE
        self.remaining_seconds = self.focus_duration
        self.completed_pomodoros = 0
        self.total_focus_seconds = 0
        
        # 回调函数
        self.on_tick = None
        self.on_state_change = None
        self.on_session_complete = None
        self.on_break_start = None
        self.on_break_end = None
        
        # 线程控制
        self._timer_thread = None
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._pause_event.set()  # 默认不暂停
    
    def set_duration(self, focus_minutes=None, short_break=None, long_break=None):
        """设置时长"""
        if focus_minutes:
            self.focus_duration = focus_minutes * 60
            if self.state == TimerState.IDLE:
                self.remaining_seconds = self.focus_duration
        
        if short_break:
            self.short_break = short_break * 60
        
        if long_break:
            self.long_break = long_break * 60
    
    def start(self):
        """开始计时"""
        if self.state == TimerState.RUNNING:
            return
        
        if self.state == TimerState.IDLE:
            self.remaining_seconds = self.focus_duration
        
        self.state = TimerState.RUNNING
        self._stop_event.clear()
        self._pause_event.set()
        
        if self.on_state_change:
            self.on_state_change(self.state)
        
        self._timer_thread = threading.Thread(target=self._run_timer, daemon=True)
        self._timer_thread.start()
    
    def pause(self):
        """暂停计时"""
        if self.state == TimerState.RUNNING:
            self.state = TimerState.PAUSED
            self._pause_event.clear()
            
            if self.on_state_change:
                self.on_state_change(self.state)
    
    def resume(self):
        """继续计时"""
        if self.state == TimerState.PAUSED:
            self.state = TimerState.RUNNING
            self._pause_event.set()
            
            if self.on_state_change:
                self.on_state_change(self.state)
    
    def stop(self):
        """停止计时"""
        self._stop_event.set()
        self._pause_event.set()  # 解除暂停以便线程退出
        
        if self._timer_thread and self._timer_thread.is_alive():
            self._timer_thread.join(timeout=1)
        
        self.state = TimerState.IDLE
        self.remaining_seconds = self.focus_duration
        
        if self.on_state_change:
            self.on_state_change(self.state)
    
    def reset(self):
        """重置计时器"""
        self.stop()
        self.completed_pomodoros = 0
        self.total_focus_seconds = 0
        self.remaining_seconds = self.focus_duration
        
        if self.on_tick:
            self.on_tick(self.remaining_seconds)
    
    def skip_break(self):
        """跳过休息"""
        if self.state == TimerState.BREAK:
            self._stop_event.set()
    
    def _run_timer(self):
        """运行计时器（线程函数）"""
        while self.remaining_seconds > 0 and not self._stop_event.is_set():
            # 检查暂停
            self._pause_event.wait()
            
            if self._stop_event.is_set():
                break
            
            time.sleep(1)
            
            if self._stop_event.is_set():
                break
            
            # 再次检查暂停（睡眠期间可能被暂停）
            if not self._pause_event.is_set():
                continue
            
            self.remaining_seconds -= 1
            
            if self.state == TimerState.RUNNING:
                self.total_focus_seconds += 1
            
            if self.on_tick:
                self.on_tick(self.remaining_seconds)
        
        # 计时结束
        if not self._stop_event.is_set():
            self._on_complete()
    
    def _on_complete(self):
        """计时完成回调"""
        if self.state == TimerState.RUNNING:
            # 专注时间结束
            self.completed_pomodoros += 1
            
            # 记录统计
            if self.data_manager:
                focus_minutes = self.focus_duration // 60
                self.data_manager.add_focus_session(focus_minutes)
            
            if self.on_session_complete:
                self.on_session_complete(self.completed_pomodoros)
            
            # 开始休息
            self._start_break()
        
        elif self.state == TimerState.BREAK:
            # 休息结束
            if self.on_break_end:
                self.on_break_end()
            
            # 重置为专注状态
            self.state = TimerState.IDLE
            self.remaining_seconds = self.focus_duration
            
            if self.on_state_change:
                self.on_state_change(self.state)
            
            if self.on_tick:
                self.on_tick(self.remaining_seconds)
    
    def _start_break(self):
        """开始休息"""
        # 判断是长休息还是短休息
        if self.completed_pomodoros % self.long_break_interval == 0:
            self.remaining_seconds = self.long_break
            break_type = "long"
        else:
            self.remaining_seconds = self.short_break
            break_type = "short"
        
        self.state = TimerState.BREAK
        
        if self.on_state_change:
            self.on_state_change(self.state)
        
        if self.on_break_start:
            self.on_break_start(break_type)
        
        if self.on_tick:
            self.on_tick(self.remaining_seconds)
        
        # 继续计时
        self._stop_event.clear()
        self._pause_event.set()
        self._timer_thread = threading.Thread(target=self._run_timer, daemon=True)
        self._timer_thread.start()
    
    def get_time_string(self):
        """获取格式化的时间字符串"""
        minutes = self.remaining_seconds // 60
        seconds = self.remaining_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def get_progress(self):
        """获取当前进度（0-1）"""
        if self.state == TimerState.BREAK:
            total = self.long_break if self.completed_pomodoros % self.long_break_interval == 0 else self.short_break
            if total == 0:
                return 0
            return 1 - (self.remaining_seconds / total)
        else:
            if self.focus_duration == 0:
                return 0
            return 1 - (self.remaining_seconds / self.focus_duration)
    
    def get_state_text(self):
        """获取状态文本"""
        state_texts = {
            TimerState.IDLE: "准备开始",
            TimerState.RUNNING: "专注中",
            TimerState.PAUSED: "已暂停",
            TimerState.BREAK: "休息中"
        }
        return state_texts.get(self.state, "未知")
