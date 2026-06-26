# 文件读写工具函数
def read_txt(file_path):
    """读取txt文件所有行"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.readlines()
    except FileNotFoundError:
        # 文件不存在就返回空列表
        return []


def write_txt(file_path, content):
    """追加文字写入txt文件"""
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(content + "\n")