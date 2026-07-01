"""
批量重命名模块
支持多种重命名规则
"""
import os
import re
from pathlib import Path


def rename_files(folder_path, rule, params, include_subfolders=False, dry_run=False):
    """
    批量重命名文件
    
    Args:
        folder_path: 文件夹路径
        rule: 重命名规则类型
            - 'prefix': 添加前缀
            - 'suffix': 添加后缀
            - 'sequence': 序号命名 (前缀+序号)
            - 'replace': 文本替换
            - 'extension': 修改扩展名
        params: 参数字典
        include_subfolders: 是否包含子文件夹
        dry_run: 试运行模式
    
    Returns:
        dict: 重命名结果
    """
    folder_path = Path(folder_path)
    if not folder_path.exists():
        raise FileNotFoundError(f"文件夹不存在: {folder_path}")
    
    # 获取所有文件
    files = []
    if include_subfolders:
        for root, dirs, filenames in os.walk(folder_path):
            for filename in filenames:
                files.append(Path(root) / filename)
    else:
        for item in folder_path.iterdir():
            if item.is_file():
                files.append(item)
    
    result = {
        "total_files": len(files),
        "renamed_files": 0,
        "failed_files": [],
        "rename_list": []
    }
    
    for index, file_path in enumerate(files):
        try:
            new_name = generate_new_name(file_path, rule, params, index)
            new_path = file_path.parent / new_name
            
            # 处理重名
            counter = 1
            while new_path.exists() and new_path != file_path:
                stem = Path(new_name).stem
                ext = Path(new_name).suffix
                new_path = file_path.parent / f"{stem}_{counter}{ext}"
                counter += 1
            
            if not dry_run:
                file_path.rename(new_path)
            
            result["renamed_files"] += 1
            result["rename_list"].append((str(file_path), str(new_path)))
        except Exception as e:
            result["failed_files"].append((str(file_path), str(e)))
    
    return result


def generate_new_name(file_path, rule, params, index=0):
    """根据规则生成新文件名"""
    original_name = file_path.name
    stem = file_path.stem
    suffix = file_path.suffix
    
    if rule == "prefix":
        prefix = params.get("prefix", "")
        return f"{prefix}{original_name}"
    
    elif rule == "suffix":
        suffix_text = params.get("suffix", "")
        return f"{stem}{suffix_text}{suffix}"
    
    elif rule == "sequence":
        prefix = params.get("prefix", "file_")
        start_num = params.get("start_num", 1)
        padding = params.get("padding", 3)
        keep_original = params.get("keep_original", False)
        
        num = start_num + index
        num_str = str(num).zfill(padding)
        
        if keep_original:
            return f"{prefix}{num_str}_{stem}{suffix}"
        else:
            return f"{prefix}{num_str}{suffix}"
    
    elif rule == "replace":
        old_text = params.get("old_text", "")
        new_text = params.get("new_text", "")
        use_regex = params.get("use_regex", False)
        
        if use_regex:
            new_stem = re.sub(old_text, new_text, stem)
        else:
            new_stem = stem.replace(old_text, new_text)
        
        return f"{new_stem}{suffix}"
    
    elif rule == "extension":
        new_extension = params.get("new_extension", "")
        if not new_extension.startswith("."):
            new_extension = "." + new_extension
        return f"{stem}{new_extension}"
    
    else:
        return original_name


def preview_rename(folder_path, rule, params, include_subfolders=False, preview_count=10):
    """预览重命名结果"""
    folder_path = Path(folder_path)
    if not folder_path.exists():
        raise FileNotFoundError(f"文件夹不存在: {folder_path}")
    
    # 获取文件
    files = []
    if include_subfolders:
        for root, dirs, filenames in os.walk(folder_path):
            for filename in filenames:
                files.append(Path(root) / filename)
                if len(files) >= preview_count:
                    break
            if len(files) >= preview_count:
                break
    else:
        for item in folder_path.iterdir():
            if item.is_file():
                files.append(item)
                if len(files) >= preview_count:
                    break
    
    preview_list = []
    for index, file_path in enumerate(files[:preview_count]):
        new_name = generate_new_name(file_path, rule, params, index)
        preview_list.append((file_path.name, new_name))
    
    return preview_list
