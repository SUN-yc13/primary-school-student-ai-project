# -*- coding: utf-8 -*-
"""
题目管理工具 v2.0
功能：
  1. 交互式单条添加题目（含难度选择）
  2. 从外部 txt 文件批量导入题目
  3. 查看题库统计
用法：
  python add_questions.py                    进入交互菜单
  python add_questions.py import <源文件> <目标题库>   批量导入
  python add_questions.py stats              查看题库统计
"""

import os
import sys
import glob

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUESTIONS_DIR = os.path.join(BASE_DIR, "questions")

DIFFICULTIES = {"1": "easy", "2": "medium", "3": "hard"}
DIFF_LABELS = {"easy": "简单", "medium": "中等", "hard": "困难"}


def ensure_dir():
    if not os.path.isdir(QUESTIONS_DIR):
        os.makedirs(QUESTIONS_DIR)


def list_files():
    ensure_dir()
    return sorted(f for f in os.listdir(QUESTIONS_DIR) if f.endswith(".txt"))


def validate_line(line):
    """校验一行题目（7字段：难度|题|A|B|C|D|答案）。"""
    parts = [p.strip() for p in line.split("|")]
    if len(parts) != 7:
        return False, f"需要7个字段（难度|题|A|B|C|D|答案），实际{len(parts)}个"
    if parts[0] not in ("easy", "medium", "hard"):
        return False, f"难度必须是 easy/medium/hard，当前是 '{parts[0]}'"
    if parts[6].upper() not in ("A", "B", "C", "D"):
        return False, f"答案必须是 A/B/C/D，当前是 '{parts[6]}'"
    if not parts[1]:
        return False, "题目内容不能为空"
    parts[6] = parts[6].upper()
    return True, "|".join(parts)


def add_single(target_file):
    print("\n--- 单条添加题目（输入 Q 取消）---")
    print("难度：1.简单  2.中等  3.困难")
    d = input("请选择难度编号：").strip()
    if d.upper() == "Q" or d not in DIFFICULTIES:
        print("已取消或难度无效。")
        return
    diff = DIFFICULTIES[d]
    q = input("题目内容：").strip()
    if q.upper() == "Q":
        return
    opts = {}
    for k in ("A", "B", "C", "D"):
        v = input(f"选项 {k}：").strip()
        if v.upper() == "Q":
            return
        opts[k] = v
    ans = input("正确答案（A/B/C/D）：").strip().upper()
    if ans == "Q" or ans not in ("A", "B", "C", "D"):
        print("答案无效，已取消。")
        return
    line = f"{diff}|{q}|{opts['A']}|{opts['B']}|{opts['C']}|{opts['D']}|{ans}"
    ok, result = validate_line(line)
    if not ok:
        print(f"校验失败：{result}")
        return
    filepath = os.path.join(QUESTIONS_DIR, target_file)
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(result + "\n")
    print(f"已添加到 {target_file}（{DIFF_LABELS[diff]}）。")


def batch_import(source_path, target_file):
    if not os.path.isfile(source_path):
        print(f"[错误] 源文件不存在：{source_path}")
        return
    ensure_dir()
    filepath = os.path.join(QUESTIONS_DIR, target_file)
    added = skipped = 0
    with open(source_path, "r", encoding="utf-8") as src, \
         open(filepath, "a", encoding="utf-8") as dst:
        for i, raw in enumerate(src, 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            ok, result = validate_line(line)
            if not ok:
                print(f"[跳过] 第{i}行：{result}")
                skipped += 1
                continue
            dst.write(result + "\n")
            added += 1
    print(f"导入完成：成功 {added} 条，跳过 {skipped} 条 → {target_file}")


def show_stats():
    files = list_files()
    if not files:
        print("题库目录为空。")
        return
    total = 0
    by_diff = {"easy": 0, "medium": 0, "hard": 0}
    print("\n" + "=" * 50)
    print(f"{'题库文件':<25}{'简单':<6}{'中等':<6}{'困难':<6}{'合计'}")
    print("-" * 50)
    for fname in files:
        f_total = 0
        f_diff = {"easy": 0, "medium": 0, "hard": 0}
        with open(os.path.join(QUESTIONS_DIR, fname), "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split("|")
                if len(parts) == 7 and parts[0] in f_diff:
                    f_diff[parts[0]] += 1
                    f_total += 1
        print(f"{fname:<25}{f_diff['easy']:<6}{f_diff['medium']:<6}"
              f"{f_diff['hard']:<6}{f_total}")
        total += f_total
        for k in by_diff:
            by_diff[k] += f_diff[k]
    print("-" * 50)
    print(f"{'总计':<25}{by_diff['easy']:<6}{by_diff['medium']:<6}"
          f"{by_diff['hard']:<6}{total}")
    print("=" * 50)


def select_target():
    files = list_files()
    print("\n现有题库：")
    for i, f in enumerate(files, 1):
        print(f"  {i}. {f}")
    print(f"  {len(files) + 1}. 新建题库文件")
    while True:
        c = input("选择目标编号：").strip()
        if c.isdigit():
            idx = int(c)
            if 1 <= idx <= len(files):
                return files[idx - 1]
            if idx == len(files) + 1:
                name = input("新题库名（不含扩展名，如 python_web）：").strip()
                if not name:
                    print("名称不能为空。")
                    continue
                target = name + ".txt"
                with open(os.path.join(QUESTIONS_DIR, target), "w", encoding="utf-8") as f:
                    f.write(f"# {name} 题库\n# 格式：难度|题目|A|B|C|D|答案\n")
                print(f"已创建 {target}")
                return target
        print("输入无效。")


def interactive_menu():
    while True:
        print("\n" + "=" * 50)
        print("           题目管理工具  v2.0")
        print("=" * 50)
        print("  1. 单条添加题目")
        print("  2. 批量导入题目")
        print("  3. 查看题库统计")
        print("  0. 退出")
        c = input("\n请选择：").strip()
        if c == "0":
            break
        elif c == "1":
            add_single(select_target())
        elif c == "2":
            src = input("源文件完整路径：").strip().strip('"')
            batch_import(src, select_target())
        elif c == "3":
            show_stats()
        else:
            print("输入无效。")


def main():
    if len(sys.argv) >= 2:
        if sys.argv[1] == "stats":
            show_stats()
            return
        if sys.argv[1] == "import" and len(sys.argv) >= 4:
            target = sys.argv[3] if sys.argv[3].endswith(".txt") else sys.argv[3] + ".txt"
            batch_import(sys.argv[2], target)
            return
    interactive_menu()


if __name__ == "__main__":
    main()
