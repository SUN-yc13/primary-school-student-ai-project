"""
桌面文件智能管理助手 - 主程序
基于 tkinter 的 Windows 原生风格界面
"""
import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path

# 导入核心模块
from organizer import organize_files, get_desktop_path, get_downloads_path
from renamer import rename_files, preview_rename
from duplicate import find_duplicate_files, get_duplicate_stats, format_size, delete_files
from largefile import scan_large_files, scan_folder_sizes, open_file_location, format_size as fmt_size


class FileManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("桌面文件智能管理助手")
        self.root.geometry("900x650")
        self.root.minsize(800, 600)
        
        # 设置Windows原生风格
        self.style = ttk.Style()
        try:
            self.style.theme_use("vista")
        except:
            try:
                self.style.theme_use("clam")
            except:
                pass
        
        self.duplicate_results = {}
        self.largefile_results = []
        
        self.create_widgets()
    
    def create_widgets(self):
        """创建主界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(
            main_frame, 
            text="桌面文件智能管理助手", 
            font=("Microsoft YaHei", 16, "bold")
        )
        title_label.pack(pady=(0, 10))
        
        # 标签页
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 创建各个功能标签页
        self.create_organizer_tab()
        self.create_renamer_tab()
        self.create_duplicate_tab()
        self.create_largefile_tab()
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(
            main_frame, 
            textvariable=self.status_var, 
            relief=tk.SUNKEN, 
            anchor=tk.W
        )
        status_bar.pack(fill=tk.X, pady=(10, 0))
    
    def create_organizer_tab(self):
        """创建文件整理标签页"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="文件整理")
        
        # 选择文件夹区域
        folder_frame = ttk.LabelFrame(tab, text="选择文件夹", padding="10")
        folder_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.org_folder_var = tk.StringVar()
        folder_entry = ttk.Entry(folder_frame, textvariable=self.org_folder_var)
        folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(folder_frame, text="浏览...", command=self.browse_org_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(folder_frame, text="桌面", command=lambda: self.org_folder_var.set(get_desktop_path())).pack(side=tk.LEFT, padx=5)
        ttk.Button(folder_frame, text="下载", command=lambda: self.org_folder_var.set(get_downloads_path())).pack(side=tk.LEFT, padx=5)
        
        # 选项区域
        options_frame = ttk.LabelFrame(tab, text="选项", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.org_subfolders_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="包含子文件夹", variable=self.org_subfolders_var).pack(side=tk.LEFT, padx=5)
        
        self.org_dryrun_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="预览模式（不实际移动）", variable=self.org_dryrun_var).pack(side=tk.LEFT, padx=20)
        
        # 操作按钮
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(btn_frame, text="开始整理", command=self.start_organize, width=15).pack(side=tk.LEFT)
        
        # 结果区域
        result_frame = ttk.LabelFrame(tab, text="整理结果", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        self.org_result_text = scrolledtext.ScrolledText(result_frame, height=15, wrap=tk.WORD)
        self.org_result_text.pack(fill=tk.BOTH, expand=True)
    
    def create_renamer_tab(self):
        """创建批量重命名标签页"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="批量重命名")
        
        # 选择文件夹
        folder_frame = ttk.LabelFrame(tab, text="选择文件夹", padding="10")
        folder_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.rename_folder_var = tk.StringVar()
        ttk.Entry(folder_frame, textvariable=self.rename_folder_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(folder_frame, text="浏览...", command=self.browse_rename_folder).pack(side=tk.LEFT)
        
        # 重命名规则
        rule_frame = ttk.LabelFrame(tab, text="重命名规则", padding="10")
        rule_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 规则类型
        ttk.Label(rule_frame, text="规则类型:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.rename_rule_var = tk.StringVar(value="prefix")
        rule_combo = ttk.Combobox(
            rule_frame, 
            textvariable=self.rename_rule_var,
            values=["prefix", "suffix", "sequence", "replace", "extension"],
            state="readonly",
            width=15
        )
        rule_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        rule_combo.bind("<<ComboboxSelected>>", self.update_rename_params)
        
        # 参数区域
        self.params_frame = ttk.Frame(rule_frame)
        self.params_frame.grid(row=1, column=0, columnspan=4, sticky=tk.W, padx=5, pady=5)
        
        # 前缀参数
        self.prefix_frame = ttk.Frame(self.params_frame)
        ttk.Label(self.prefix_frame, text="前缀:").pack(side=tk.LEFT, padx=5)
        self.prefix_var = tk.StringVar(value="new_")
        ttk.Entry(self.prefix_frame, textvariable=self.prefix_var, width=20).pack(side=tk.LEFT)
        
        # 后缀参数
        self.suffix_frame = ttk.Frame(self.params_frame)
        ttk.Label(self.suffix_frame, text="后缀:").pack(side=tk.LEFT, padx=5)
        self.suffix_var = tk.StringVar(value="_backup")
        ttk.Entry(self.suffix_frame, textvariable=self.suffix_var, width=20).pack(side=tk.LEFT)
        
        # 序号参数
        self.sequence_frame = ttk.Frame(self.params_frame)
        ttk.Label(self.sequence_frame, text="前缀:").pack(side=tk.LEFT, padx=5)
        self.seq_prefix_var = tk.StringVar(value="file_")
        ttk.Entry(self.sequence_frame, textvariable=self.seq_prefix_var, width=10).pack(side=tk.LEFT)
        ttk.Label(self.sequence_frame, text="起始:").pack(side=tk.LEFT, padx=5)
        self.seq_start_var = tk.StringVar(value="1")
        ttk.Entry(self.sequence_frame, textvariable=self.seq_start_var, width=5).pack(side=tk.LEFT)
        ttk.Label(self.sequence_frame, text="位数:").pack(side=tk.LEFT, padx=5)
        self.seq_padding_var = tk.StringVar(value="3")
        ttk.Entry(self.sequence_frame, textvariable=self.seq_padding_var, width=5).pack(side=tk.LEFT)
        self.seq_keep_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.sequence_frame, text="保留原名", variable=self.seq_keep_var).pack(side=tk.LEFT, padx=10)
        
        # 替换参数
        self.replace_frame = ttk.Frame(self.params_frame)
        ttk.Label(self.replace_frame, text="查找:").pack(side=tk.LEFT, padx=5)
        self.replace_old_var = tk.StringVar()
        ttk.Entry(self.replace_frame, textvariable=self.replace_old_var, width=15).pack(side=tk.LEFT)
        ttk.Label(self.replace_frame, text="替换为:").pack(side=tk.LEFT, padx=5)
        self.replace_new_var = tk.StringVar()
        ttk.Entry(self.replace_frame, textvariable=self.replace_new_var, width=15).pack(side=tk.LEFT)
        self.replace_regex_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.replace_frame, text="使用正则", variable=self.replace_regex_var).pack(side=tk.LEFT, padx=10)
        
        # 扩展名参数
        self.extension_frame = ttk.Frame(self.params_frame)
        ttk.Label(self.extension_frame, text="新扩展名:").pack(side=tk.LEFT, padx=5)
        self.new_ext_var = tk.StringVar(value="txt")
        ttk.Entry(self.extension_frame, textvariable=self.new_ext_var, width=10).pack(side=tk.LEFT)
        
        # 选项
        options_frame = ttk.Frame(rule_frame)
        options_frame.grid(row=2, column=0, columnspan=4, sticky=tk.W, padx=5, pady=5)
        
        self.rename_subfolders_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="包含子文件夹", variable=self.rename_subfolders_var).pack(side=tk.LEFT, padx=5)
        
        # 操作按钮
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(btn_frame, text="预览", command=self.preview_rename, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="开始重命名", command=self.start_rename, width=15).pack(side=tk.LEFT, padx=5)
        
        # 预览/结果区域
        result_frame = ttk.LabelFrame(tab, text="预览/结果", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建表格
        columns = ("original", "new")
        self.rename_tree = ttk.Treeview(result_frame, columns=columns, show="headings")
        self.rename_tree.heading("original", text="原文件名")
        self.rename_tree.heading("new", text="新文件名")
        self.rename_tree.column("original", width=300)
        self.rename_tree.column("new", width=300)
        
        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.rename_tree.yview)
        self.rename_tree.configure(yscrollcommand=scrollbar.set)
        
        self.rename_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 初始化显示前缀参数
        self.update_rename_params()
    
    def create_duplicate_tab(self):
        """创建重复文件检测标签页"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="重复文件检测")
        
        # 选择文件夹
        folder_frame = ttk.LabelFrame(tab, text="选择文件夹", padding="10")
        folder_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.dup_folder_var = tk.StringVar()
        ttk.Entry(folder_frame, textvariable=self.dup_folder_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(folder_frame, text="浏览...", command=self.browse_dup_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(folder_frame, text="桌面", command=lambda: self.dup_folder_var.set(get_desktop_path())).pack(side=tk.LEFT, padx=5)
        
        # 选项
        options_frame = ttk.LabelFrame(tab, text="选项", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.dup_subfolders_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="包含子文件夹", variable=self.dup_subfolders_var).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(options_frame, text="最小文件大小(KB):").pack(side=tk.LEFT, padx=(20, 5))
        self.dup_minsize_var = tk.StringVar(value="0")
        ttk.Entry(options_frame, textvariable=self.dup_minsize_var, width=10).pack(side=tk.LEFT)
        
        # 操作按钮
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(btn_frame, text="开始扫描", command=self.start_duplicate_scan, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="删除选中", command=self.delete_selected_duplicates, width=15).pack(side=tk.LEFT, padx=5)
        
        # 统计信息
        self.dup_stats_var = tk.StringVar(value="等待扫描...")
        stats_label = ttk.Label(tab, textvariable=self.dup_stats_var, foreground="blue")
        stats_label.pack(fill=tk.X, pady=(0, 5))
        
        # 结果区域
        result_frame = ttk.LabelFrame(tab, text="重复文件列表", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建树形视图
        self.dup_tree = ttk.Treeview(result_frame, show="tree headings", columns=("size", "path"))
        self.dup_tree.heading("#0", text="文件组")
        self.dup_tree.heading("size", text="大小")
        self.dup_tree.heading("path", text="路径")
        self.dup_tree.column("#0", width=200)
        self.dup_tree.column("size", width=100)
        self.dup_tree.column("path", width=400)
        
        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.dup_tree.yview)
        self.dup_tree.configure(yscrollcommand=scrollbar.set)
        
        self.dup_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_largefile_tab(self):
        """创建大文件扫描标签页"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="大文件扫描")
        
        # 选择文件夹
        folder_frame = ttk.LabelFrame(tab, text="选择文件夹", padding="10")
        folder_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.large_folder_var = tk.StringVar()
        ttk.Entry(folder_frame, textvariable=self.large_folder_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(folder_frame, text="浏览...", command=self.browse_large_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(folder_frame, text="C盘", command=lambda: self.large_folder_var.set("C:\\")).pack(side=tk.LEFT, padx=5)
        
        # 选项
        options_frame = ttk.LabelFrame(tab, text="选项", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(options_frame, text="最小文件大小(MB):").pack(side=tk.LEFT, padx=5)
        self.large_minsize_var = tk.StringVar(value="100")
        ttk.Entry(options_frame, textvariable=self.large_minsize_var, width=10).pack(side=tk.LEFT, padx=5)
        
        self.large_subfolders_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="包含子文件夹", variable=self.large_subfolders_var).pack(side=tk.LEFT, padx=20)
        
        # 操作按钮
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(btn_frame, text="扫描大文件", command=self.start_largefile_scan, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="扫描文件夹大小", command=self.start_folder_size_scan, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="打开位置", command=self.open_selected_file, width=10).pack(side=tk.LEFT, padx=5)
        
        # 结果区域
        result_frame = ttk.LabelFrame(tab, text="扫描结果", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建表格
        columns = ("name", "size", "path")
        self.large_tree = ttk.Treeview(result_frame, columns=columns, show="headings")
        self.large_tree.heading("name", text="名称")
        self.large_tree.heading("size", text="大小")
        self.large_tree.heading("path", text="路径")
        self.large_tree.column("name", width=200)
        self.large_tree.column("size", width=100)
        self.large_tree.column("path", width=400)
        
        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.large_tree.yview)
        self.large_tree.configure(yscrollcommand=scrollbar.set)
        
        self.large_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # ========== 文件夹浏览函数 ==========
    def browse_org_folder(self):
        folder = filedialog.askdirectory(title="选择要整理的文件夹")
        if folder:
            self.org_folder_var.set(folder)
    
    def browse_rename_folder(self):
        folder = filedialog.askdirectory(title="选择要重命名的文件夹")
        if folder:
            self.rename_folder_var.set(folder)
    
    def browse_dup_folder(self):
        folder = filedialog.askdirectory(title="选择要扫描的文件夹")
        if folder:
            self.dup_folder_var.set(folder)
    
    def browse_large_folder(self):
        folder = filedialog.askdirectory(title="选择要扫描的文件夹")
        if folder:
            self.large_folder_var.set(folder)
    
    # ========== 文件整理功能 ==========
    def start_organize(self):
        folder = self.org_folder_var.get()
        if not folder or not os.path.exists(folder):
            messagebox.showwarning("提示", "请选择有效的文件夹")
            return
        
        if not self.org_dryrun_var.get():
            confirm = messagebox.askyesno("确认", "确定要整理该文件夹吗？文件将被移动到分类文件夹中。")
            if not confirm:
                return
        
        self.status_var.set("正在整理文件...")
        self.root.update()
        
        def run():
            try:
                result = organize_files(
                    folder,
                    include_subfolders=self.org_subfolders_var.get(),
                    dry_run=self.org_dryrun_var.get()
                )
                
                self.root.after(0, lambda: self.show_organize_result(result))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("错误", str(e)))
                self.root.after(0, lambda: self.status_var.set("出错"))
        
        threading.Thread(target=run, daemon=True).start()
    
    def show_organize_result(self, result):
        self.org_result_text.delete(1.0, tk.END)
        
        mode = "预览模式" if result["moved_files"] == result.get("total_files", 0) and False else "实际执行"
        self.org_result_text.insert(tk.END, f"整理完成！\n\n")
        self.org_result_text.insert(tk.END, f"总文件数: {result['total_files']}\n")
        self.org_result_text.insert(tk.END, f"已移动文件: {result['moved_files']}\n\n")
        
        self.org_result_text.insert(tk.END, "分类统计:\n")
        self.org_result_text.insert(tk.END, "-" * 30 + "\n")
        for category, count in sorted(result["categories"].items(), key=lambda x: x[1], reverse=True):
            self.org_result_text.insert(tk.END, f"  {category}: {count} 个文件\n")
        
        if result["failed_files"]:
            self.org_result_text.insert(tk.END, f"\n失败文件 ({len(result['failed_files'])} 个):\n")
            for path, error in result["failed_files"]:
                self.org_result_text.insert(tk.END, f"  {path}: {error}\n")
        
        self.status_var.set(f"整理完成，移动了 {result['moved_files']} 个文件")
    
    # ========== 批量重命名功能 ==========
    def update_rename_params(self, event=None):
        """更新重命名参数显示"""
        # 隐藏所有参数框架
        for frame in [self.prefix_frame, self.suffix_frame, self.sequence_frame, self.replace_frame, self.extension_frame]:
            frame.pack_forget()
        
        rule = self.rename_rule_var.get()
        if rule == "prefix":
            self.prefix_frame.pack(side=tk.LEFT)
        elif rule == "suffix":
            self.suffix_frame.pack(side=tk.LEFT)
        elif rule == "sequence":
            self.sequence_frame.pack(side=tk.LEFT)
        elif rule == "replace":
            self.replace_frame.pack(side=tk.LEFT)
        elif rule == "extension":
            self.extension_frame.pack(side=tk.LEFT)
    
    def get_rename_params(self):
        """获取当前重命名参数"""
        rule = self.rename_rule_var.get()
        params = {}
        
        if rule == "prefix":
            params["prefix"] = self.prefix_var.get()
        elif rule == "suffix":
            params["suffix"] = self.suffix_var.get()
        elif rule == "sequence":
            params["prefix"] = self.seq_prefix_var.get()
            try:
                params["start_num"] = int(self.seq_start_var.get())
            except:
                params["start_num"] = 1
            try:
                params["padding"] = int(self.seq_padding_var.get())
            except:
                params["padding"] = 3
            params["keep_original"] = self.seq_keep_var.get()
        elif rule == "replace":
            params["old_text"] = self.replace_old_var.get()
            params["new_text"] = self.replace_new_var.get()
            params["use_regex"] = self.replace_regex_var.get()
        elif rule == "extension":
            params["new_extension"] = self.new_ext_var.get()
        
        return rule, params
    
    def preview_rename(self):
        folder = self.rename_folder_var.get()
        if not folder or not os.path.exists(folder):
            messagebox.showwarning("提示", "请选择有效的文件夹")
            return
        
        rule, params = self.get_rename_params()
        
        try:
            preview_list = preview_rename(
                folder, rule, params,
                include_subfolders=self.rename_subfolders_var.get(),
                preview_count=20
            )
            
            # 清空表格
            for item in self.rename_tree.get_children():
                self.rename_tree.delete(item)
            
            # 填充预览数据
            for original, new_name in preview_list:
                self.rename_tree.insert("", tk.END, values=(original, new_name))
            
            self.status_var.set(f"预览完成，显示前 {len(preview_list)} 个文件")
        except Exception as e:
            messagebox.showerror("错误", str(e))
    
    def start_rename(self):
        folder = self.rename_folder_var.get()
        if not folder or not os.path.exists(folder):
            messagebox.showwarning("提示", "请选择有效的文件夹")
            return
        
        confirm = messagebox.askyesno("确认", "确定要批量重命名吗？此操作不可撤销。")
        if not confirm:
            return
        
        rule, params = self.get_rename_params()
        
        self.status_var.set("正在重命名...")
        self.root.update()
        
        def run():
            try:
                result = rename_files(
                    folder, rule, params,
                    include_subfolders=self.rename_subfolders_var.get()
                )
                self.root.after(0, lambda: self.show_rename_result(result))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("错误", str(e)))
                self.root.after(0, lambda: self.status_var.set("出错"))
        
        threading.Thread(target=run, daemon=True).start()
    
    def show_rename_result(self, result):
        # 清空表格
        for item in self.rename_tree.get_children():
            self.rename_tree.delete(item)
        
        # 填充结果数据
        for original, new_path in result["rename_list"]:
            original_name = os.path.basename(original)
            new_name = os.path.basename(new_path)
            self.rename_tree.insert("", tk.END, values=(original_name, new_name))
        
        self.status_var.set(f"重命名完成，成功 {result['renamed_files']} 个，失败 {len(result['failed_files'])} 个")
        
        if result["failed_files"]:
            messagebox.showwarning("部分失败", f"有 {len(result['failed_files'])} 个文件重命名失败")
    
    # ========== 重复文件检测功能 ==========
    def start_duplicate_scan(self):
        folder = self.dup_folder_var.get()
        if not folder or not os.path.exists(folder):
            messagebox.showwarning("提示", "请选择有效的文件夹")
            return
        
        try:
            min_size = int(self.dup_minsize_var.get()) * 1024  # KB转字节
        except:
            min_size = 0
        
        self.status_var.set("正在扫描重复文件...")
        self.root.update()
        
        def progress_callback(current, total, status):
            self.root.after(0, lambda: self.status_var.set(status))
        
        def run():
            try:
                duplicates = find_duplicate_files(
                    folder,
                    include_subfolders=self.dup_subfolders_var.get(),
                    min_size=min_size,
                    progress_callback=progress_callback
                )
                self.root.after(0, lambda: self.show_duplicate_results(duplicates))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("错误", str(e)))
                self.root.after(0, lambda: self.status_var.set("出错"))
        
        threading.Thread(target=run, daemon=True).start()
    
    def show_duplicate_results(self, duplicates):
        self.duplicate_results = duplicates
        
        # 清空树形视图
        for item in self.dup_tree.get_children():
            self.dup_tree.delete(item)
        
        # 填充数据
        for i, (file_hash, files) in enumerate(duplicates.items(), 1):
            size_str = format_size(files[0]["size"])
            group_id = f"group_{i}"
            self.dup_tree.insert(
                "", tk.END, group_id,
                text=f"第 {i} 组 ({len(files)} 个文件)",
                values=(size_str, "")
            )
            
            for j, file_info in enumerate(files):
                item_id = f"{group_id}_{j}"
                self.dup_tree.insert(
                    group_id, tk.END, item_id,
                    text=file_info["name"],
                    values=(size_str, file_info["path"]),
                    tags=("file",)
                )
        
        # 统计信息
        stats = get_duplicate_stats(duplicates)
        self.dup_stats_var.set(
            f"找到 {stats['duplicate_groups']} 组重复文件，"
            f"共 {stats['duplicate_files']} 个重复文件，"
            f"可释放空间: {stats['wasted_space_human']}"
        )
        
        self.status_var.set(f"扫描完成，找到 {len(duplicates)} 组重复文件")
    
    def delete_selected_duplicates(self):
        selected = self.dup_tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请选择要删除的文件")
            return
        
        # 收集选中的文件路径
        file_paths = []
        for item_id in selected:
            item = self.dup_tree.item(item_id)
            if "file" in item.get("tags", []):
                file_path = item["values"][1]
                file_paths.append(file_path)
        
        if not file_paths:
            messagebox.showwarning("提示", "请选择具体的文件（不是文件组）")
            return
        
        confirm = messagebox.askyesno(
            "确认删除",
            f"确定要删除选中的 {len(file_paths)} 个文件吗？\n建议保留每组中的一个文件。"
        )
        if not confirm:
            return
        
        result = delete_files(file_paths, move_to_trash=True)
        
        messagebox.showinfo(
            "删除结果",
            f"成功删除 {len(result['success'])} 个文件\n失败 {len(result['failed'])} 个文件"
        )
        
        # 重新扫描
        if self.dup_folder_var.get():
            self.start_duplicate_scan()
    
    # ========== 大文件扫描功能 ==========
    def start_largefile_scan(self):
        folder = self.large_folder_var.get()
        if not folder or not os.path.exists(folder):
            messagebox.showwarning("提示", "请选择有效的文件夹")
            return
        
        try:
            min_size_mb = int(self.large_minsize_var.get())
        except:
            min_size_mb = 100
        
        self.status_var.set("正在扫描大文件...")
        self.root.update()
        
        def progress_callback(current, total, status):
            self.root.after(0, lambda: self.status_var.set(status))
        
        def run():
            try:
                large_files = scan_large_files(
                    folder,
                    min_size_mb=min_size_mb,
                    include_subfolders=self.large_subfolders_var.get(),
                    progress_callback=progress_callback
                )
                self.root.after(0, lambda: self.show_largefile_results(large_files))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("错误", str(e)))
                self.root.after(0, lambda: self.status_var.set("出错"))
        
        threading.Thread(target=run, daemon=True).start()
    
    def start_folder_size_scan(self):
        folder = self.large_folder_var.get()
        if not folder or not os.path.exists(folder):
            messagebox.showwarning("提示", "请选择有效的文件夹")
            return
        
        self.status_var.set("正在计算文件夹大小...")
        self.root.update()
        
        def progress_callback(current, total, status):
            self.root.after(0, lambda: self.status_var.set(status))
        
        def run():
            try:
                folder_sizes = scan_folder_sizes(folder, progress_callback)
                self.root.after(0, lambda: self.show_folder_size_results(folder_sizes))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("错误", str(e)))
                self.root.after(0, lambda: self.status_var.set("出错"))
        
        threading.Thread(target=run, daemon=True).start()
    
    def show_largefile_results(self, files):
        self.largefile_results = files
        
        # 清空表格
        for item in self.large_tree.get_children():
            self.large_tree.delete(item)
        
        # 填充数据
        for file_info in files:
            self.large_tree.insert(
                "", tk.END,
                values=(file_info["name"], file_info["size_human"], file_info["path"])
            )
        
        total_size = sum(f["size"] for f in files)
        self.status_var.set(f"找到 {len(files)} 个大文件，总计 {format_size(total_size)}")
    
    def show_folder_size_results(self, folders):
        # 清空表格
        for item in self.large_tree.get_children():
            self.large_tree.delete(item)
        
        # 填充数据
        for folder_info in folders:
            self.large_tree.insert(
                "", tk.END,
                values=(
                    f"[文件夹] {folder_info['name']}",
                    folder_info["total_size_human"],
                    folder_info["path"]
                )
            )
        
        self.status_var.set(f"扫描完成，共 {len(folders)} 个文件夹")
    
    def open_selected_file(self):
        selected = self.large_tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请选择一个文件或文件夹")
            return
        
        item = self.large_tree.item(selected[0])
        path = item["values"][2]
        
        if os.path.exists(path):
            open_file_location(path)
        else:
            messagebox.showwarning("提示", "路径不存在")


def main():
    root = tk.Tk()
    app = FileManagerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
