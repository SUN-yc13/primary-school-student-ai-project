"""
重复文件检测模块
通过MD5哈希值识别重复文件
"""
import os
import hashlib
from pathlib import Path
from collections import defaultdict


def get_file_hash(file_path, chunk_size=8192):
    """计算文件的MD5哈希值"""
    md5_hash = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                md5_hash.update(chunk)
        return md5_hash.hexdigest()
    except Exception as e:
        return None


def get_file_size(file_path):
    """获取文件大小（字节）"""
    try:
        return os.path.getsize(file_path)
    except Exception:
        return -1


def find_duplicate_files(folder_path, include_subfolders=True, min_size=0, progress_callback=None):
    """
    查找重复文件
    
    Args:
        folder_path: 要扫描的文件夹路径
        include_subfolders: 是否包含子文件夹
        min_size: 最小文件大小（字节），小于此大小的文件将被忽略
        progress_callback: 进度回调函数 (current, total, status)
    
    Returns:
        dict: 重复文件分组，key为文件哈希，value为文件路径列表
    """
    folder_path = Path(folder_path)
    if not folder_path.exists():
        raise FileNotFoundError(f"文件夹不存在: {folder_path}")
    
    # 第一步：收集所有文件并按大小分组
    if progress_callback:
        progress_callback(0, 0, "正在扫描文件...")
    
    size_groups = defaultdict(list)
    total_files = 0
    
    if include_subfolders:
        for root, dirs, filenames in os.walk(folder_path):
            for filename in filenames:
                file_path = Path(root) / filename
                file_size = get_file_size(file_path)
                if file_size >= min_size and file_size > 0:
                    size_groups[file_size].append(file_path)
                    total_files += 1
    else:
        for item in folder_path.iterdir():
            if item.is_file():
                file_size = get_file_size(item)
                if file_size >= min_size and file_size > 0:
                    size_groups[file_size].append(item)
                    total_files += 1
    
    # 只保留有重复大小的文件组
    candidate_groups = {size: paths for size, paths in size_groups.items() if len(paths) > 1}
    
    if progress_callback:
        progress_callback(0, total_files, f"找到 {total_files} 个文件，正在计算哈希...")
    
    # 第二步：对候选文件计算哈希
    hash_groups = defaultdict(list)
    processed = 0
    
    for size, paths in candidate_groups.items():
        for file_path in paths:
            file_hash = get_file_hash(file_path)
            if file_hash:
                hash_groups[file_hash].append({
                    "path": str(file_path),
                    "size": size,
                    "name": file_path.name
                })
            processed += 1
            if progress_callback and processed % 10 == 0:
                progress_callback(processed, total_files, f"正在计算哈希... {processed}/{total_files}")
    
    # 第三步：只保留有重复哈希的分组
    duplicate_groups = {h: files for h, files in hash_groups.items() if len(files) > 1}
    
    if progress_callback:
        progress_callback(total_files, total_files, f"扫描完成，找到 {len(duplicate_groups)} 组重复文件")
    
    return duplicate_groups


def get_duplicate_stats(duplicate_groups):
    """获取重复文件统计信息"""
    total_duplicates = 0
    total_wasted_space = 0
    
    for file_hash, files in duplicate_groups.items():
        # 保留一个，其余都是重复的
        dup_count = len(files) - 1
        total_duplicates += dup_count
        total_wasted_space += dup_count * files[0]["size"]
    
    return {
        "duplicate_groups": len(duplicate_groups),
        "duplicate_files": total_duplicates,
        "wasted_space": total_wasted_space,
        "wasted_space_human": format_size(total_wasted_space)
    }


def format_size(size_bytes):
    """格式化文件大小为人类可读格式"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def delete_files(file_paths, move_to_trash=True):
    """
    删除文件
    
    Args:
        file_paths: 文件路径列表
        move_to_trash: 是否移动到回收站（True: 回收站, False: 直接删除）
    
    Returns:
        dict: 删除结果
    """
    result = {
        "success": [],
        "failed": []
    }
    
    for file_path in file_paths:
        try:
            if move_to_trash:
                try:
                    # 尝试使用send2trash库
                    from send2trash import send2trash
                    send2trash(file_path)
                except ImportError:
                    # 如果没有send2trash，直接删除
                    os.remove(file_path)
            else:
                os.remove(file_path)
            result["success"].append(file_path)
        except Exception as e:
            result["failed"].append((file_path, str(e)))
    
    return result
