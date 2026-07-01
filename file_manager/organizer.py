"""
文件整理模块
按文件类型自动分类整理文件
"""
import os
import shutil
from pathlib import Path

# 文件类型分类规则
FILE_CATEGORIES = {
    "图片": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".svg", ".ico", ".raw", ".heic"],
    "文档": [".txt", ".doc", ".docx", ".pdf", ".xls", ".xlsx", ".ppt", ".pptx", ".csv", ".rtf", ".odt", ".ods", ".odp", ".md", ".epub"],
    "视频": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".mpeg", ".mpg"],
    "音频": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a", ".aiff", ".opus"],
    "压缩包": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".iso"],
    "程序": [".exe", ".msi", ".bat", ".sh", ".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".h", ".dll", ".sys"],
    "安装包": [".exe", ".msi", ".apk", ".dmg", ".pkg", ".deb", ".rpm"],
}


def get_category(file_extension):
    """根据文件扩展名获取分类"""
    file_extension = file_extension.lower()
    for category, extensions in FILE_CATEGORIES.items():
        if file_extension in extensions:
            return category
    return "其他"


def scan_files(folder_path, include_subfolders=False):
    """扫描文件夹中的所有文件"""
    files = []
    folder_path = Path(folder_path)
    
    if include_subfolders:
        for root, dirs, filenames in os.walk(folder_path):
            for filename in filenames:
                file_path = Path(root) / filename
                files.append(file_path)
    else:
        for item in folder_path.iterdir():
            if item.is_file():
                files.append(item)
    
    return files


def organize_files(folder_path, include_subfolders=False, dry_run=False):
    """
    整理文件：按类型分类移动到对应文件夹
    
    Args:
        folder_path: 要整理的文件夹路径
        include_subfolders: 是否包含子文件夹
        dry_run: 试运行模式，只返回计划不实际移动
    
    Returns:
        dict: 整理结果统计
    """
    folder_path = Path(folder_path)
    if not folder_path.exists():
        raise FileNotFoundError(f"文件夹不存在: {folder_path}")
    
    files = scan_files(folder_path, include_subfolders)
    
    # 过滤掉已经在分类文件夹中的文件
    category_names = list(FILE_CATEGORIES.keys()) + ["其他"]
    files = [f for f in files if f.parent.name not in category_names]
    
    result = {
        "total_files": len(files),
        "moved_files": 0,
        "categories": {},
        "failed_files": [],
        "moved_list": []
    }
    
    for file_path in files:
        category = get_category(file_path.suffix)
        target_folder = folder_path / category
        
        if category not in result["categories"]:
            result["categories"][category] = 0
        
        # 创建目标文件夹
        if not dry_run and not target_folder.exists():
            target_folder.mkdir(exist_ok=True)
        
        target_path = target_folder / file_path.name
        
        # 处理重名文件
        counter = 1
        while target_path.exists():
            name_without_ext = file_path.stem
            extension = file_path.suffix
            target_path = target_folder / f"{name_without_ext}_{counter}{extension}"
            counter += 1
        
        try:
            if not dry_run:
                shutil.move(str(file_path), str(target_path))
            result["moved_files"] += 1
            result["categories"][category] += 1
            result["moved_list"].append((str(file_path), str(target_path)))
        except Exception as e:
            result["failed_files"].append((str(file_path), str(e)))
    
    return result


def get_desktop_path():
    """获取桌面路径"""
    return str(Path.home() / "Desktop")


def get_downloads_path():
    """获取下载文件夹路径"""
    return str(Path.home() / "Downloads")
