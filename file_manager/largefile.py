"""
大文件扫描模块
扫描并定位大文件，帮助释放磁盘空间
"""
import os
from pathlib import Path


def scan_large_files(folder_path, min_size_mb=100, include_subfolders=True, progress_callback=None):
    """
    扫描大文件
    
    Args:
        folder_path: 要扫描的文件夹路径
        min_size_mb: 最小文件大小（MB）
        include_subfolders: 是否包含子文件夹
        progress_callback: 进度回调函数
    
    Returns:
        list: 大文件列表，按大小降序排列
    """
    folder_path = Path(folder_path)
    if not folder_path.exists():
        raise FileNotFoundError(f"文件夹不存在: {folder_path}")
    
    min_size_bytes = min_size_mb * 1024 * 1024
    large_files = []
    total_scanned = 0
    
    if progress_callback:
        progress_callback(0, 0, "正在扫描...")
    
    if include_subfolders:
        for root, dirs, filenames in os.walk(folder_path):
            for filename in filenames:
                file_path = Path(root) / filename
                try:
                    file_size = os.path.getsize(file_path)
                    if file_size >= min_size_bytes:
                        large_files.append({
                            "path": str(file_path),
                            "name": filename,
                            "size": file_size,
                            "size_human": format_size(file_size),
                            "folder": str(file_path.parent)
                        })
                    total_scanned += 1
                    if progress_callback and total_scanned % 100 == 0:
                        progress_callback(total_scanned, 0, f"已扫描 {total_scanned} 个文件...")
                except (OSError, PermissionError):
                    continue
    else:
        for item in folder_path.iterdir():
            if item.is_file():
                try:
                    file_size = os.path.getsize(item)
                    if file_size >= min_size_bytes:
                        large_files.append({
                            "path": str(item),
                            "name": item.name,
                            "size": file_size,
                            "size_human": format_size(file_size),
                            "folder": str(item.parent)
                        })
                    total_scanned += 1
                except (OSError, PermissionError):
                    continue
    
    # 按大小降序排列
    large_files.sort(key=lambda x: x["size"], reverse=True)
    
    if progress_callback:
        progress_callback(total_scanned, total_scanned, f"扫描完成，找到 {len(large_files)} 个大文件")
    
    return large_files


def get_folder_size(folder_path, progress_callback=None):
    """
    计算文件夹总大小
    
    Args:
        folder_path: 文件夹路径
        progress_callback: 进度回调函数
    
    Returns:
        dict: 文件夹大小信息
    """
    folder_path = Path(folder_path)
    if not folder_path.exists():
        raise FileNotFoundError(f"文件夹不存在: {folder_path}")
    
    total_size = 0
    file_count = 0
    folder_count = 0
    
    for root, dirs, filenames in os.walk(folder_path):
        folder_count += len(dirs)
        for filename in filenames:
            file_path = Path(root) / filename
            try:
                total_size += os.path.getsize(file_path)
                file_count += 1
            except (OSError, PermissionError):
                continue
    
    return {
        "path": str(folder_path),
        "name": folder_path.name,
        "total_size": total_size,
        "total_size_human": format_size(total_size),
        "file_count": file_count,
        "folder_count": folder_count
    }


def scan_folder_sizes(folder_path, progress_callback=None):
    """
    扫描子文件夹大小
    
    Args:
        folder_path: 父文件夹路径
        progress_callback: 进度回调函数
    
    Returns:
        list: 子文件夹大小列表，按大小降序排列
    """
    folder_path = Path(folder_path)
    if not folder_path.exists():
        raise FileNotFoundError(f"文件夹不存在: {folder_path}")
    
    folder_sizes = []
    
    # 先获取所有子文件夹
    subfolders = [item for item in folder_path.iterdir() if item.is_dir()]
    total = len(subfolders)
    
    for i, subfolder in enumerate(subfolders):
        try:
            size_info = get_folder_size(subfolder)
            folder_sizes.append(size_info)
        except Exception:
            continue
        
        if progress_callback:
            progress_callback(i + 1, total, f"正在计算 {subfolder.name} 的大小...")
    
    # 按大小降序排列
    folder_sizes.sort(key=lambda x: x["total_size"], reverse=True)
    
    return folder_sizes


def format_size(size_bytes):
    """格式化文件大小为人类可读格式"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    elif size_bytes < 1024 * 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024 * 1024):.2f} TB"


def open_file_location(file_path):
    """在文件资源管理器中打开文件所在位置"""
    import subprocess
    import sys
    
    try:
        if sys.platform == "win32":
            # Windows
            subprocess.run(["explorer", "/select,", file_path])
        elif sys.platform == "darwin":
            # macOS
            subprocess.run(["open", "-R", file_path])
        else:
            # Linux
            subprocess.run(["xdg-open", os.path.dirname(file_path)])
        return True
    except Exception:
        return False
