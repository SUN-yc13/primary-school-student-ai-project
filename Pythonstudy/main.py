# -*- coding: utf-8 -*-
"""
Python 考试系统 - 主程序 v2.0
功能：
  1. 随机考试（支持题量选择 + 难度筛选）
  2. 错题回顾（从错题本抽题重做）
  3. 历史记录（查看历次考试成绩）
  4. 自动记录错题与考试历史
退出：所有界面结束后按 ESC 关闭窗口。
"""

import os
import json
import time
import random
import glob
import shutil
from datetime import datetime

# ── 路径配置 ──────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUESTIONS_DIR = os.path.join(BASE_DIR, "questions")
DATA_DIR = os.path.join(BASE_DIR, "data")
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")
WRONG_FILE = os.path.join(DATA_DIR, "wrong_questions.json")

# ── 常量配置 ──────────────────────────────────────────────────────────────────
QUIZ_OPTIONS = [3, 5, 20, 50, 100]
DIFFICULTY_LEVELS = {
    "1": ("all", "全部难度"),
    "2": ("easy", "简单"),
    "3": ("medium", "中等"),
    "4": ("hard", "困难"),
}


# ══════════════════════════════════════════════════════════════════════════════
#  数据持久化层
# ══════════════════════════════════════════════════════════════════════════════

def ensure_data_dir():
    if not os.path.isdir(DATA_DIR):
        os.makedirs(DATA_DIR)


def load_json(filepath, default):
    if not os.path.isfile(filepath):
        return default
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return default


def save_json(filepath, data):
    ensure_data_dir()
    tmp_path = filepath + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    # 如果原文件存在，先备份
    if os.path.isfile(filepath):
        bak_path = filepath + ".bak"
        shutil.copy2(filepath, bak_path)
    # 原子替换
    os.replace(tmp_path, filepath)


# ══════════════════════════════════════════════════════════════════════════════
#  题库加载
# ══════════════════════════════════════════════════════════════════════════════

def load_questions(questions_dir, difficulty_filter="all"):
    """加载 questions 目录下所有 .txt 题库，按难度筛选。
    格式：难度|题目|A|B|C|D|答案
    """
    questions = []
    if not os.path.isdir(questions_dir):
        print(f"[错误] 题库目录不存在：{questions_dir}")
        return questions

    txt_files = sorted(glob.glob(os.path.join(questions_dir, "*.txt")))
    if not txt_files:
        print("[错误] questions 目录下没有找到任何 .txt 题库文件。")
        return questions

    for filepath in txt_files:
        filename = os.path.basename(filepath)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                for line_no, raw in enumerate(f, 1):
                    line = raw.strip()
                    if not line or line.startswith("#"):
                        continue
                    parts = [p.strip() for p in line.split("|")]
                    if len(parts) != 8:
                        print(f"[警告] {filename} 第{line_no}行字段数错误（需8个），已跳过")
                        continue
                    diff, q_text, a, b, c, d, answer, qid = parts
                    answer = answer.upper()
                    if answer not in ("A", "B", "C", "D"):
                        print(f"[警告] {filename} 第{line_no}行答案无效，已跳过")
                        continue
                    if difficulty_filter != "all" and diff != difficulty_filter:
                        continue
                    questions.append({
                        "difficulty": diff,
                        "question": q_text,
                        "options": {"A": a, "B": b, "C": c, "D": d},
                        "answer": answer,
                        "id": qid,
                        "source": filename,
                    })
        except Exception as e:
            print(f"[错误] 读取 {filename} 失败：{e}")
    return questions


def question_to_dict(q):
    """把题目对象转为可 JSON 序列化的 dict。"""
    return {
        "difficulty": q["difficulty"],
        "question": q["question"],
        "options": q["options"],
        "answer": q["answer"],
        "id": q.get("id", ""),
        "source": q["source"],
    }


# ══════════════════════════════════════════════════════════════════════════════
#  错题本管理
# ══════════════════════════════════════════════════════════════════════════════

def load_wrong_questions():
    return load_json(WRONG_FILE, [])


def save_wrong_questions(wrong_list):
    save_json(WRONG_FILE, wrong_list)


def add_to_wrong_book(question):
    """把答错的题加入错题本，重复题目累计错误次数。"""
    wrong_list = load_wrong_questions()
    qid = question.get("id", "")
    for item in wrong_list:
        if item.get("id", "") == qid and qid:
            item["wrong_count"] = item.get("wrong_count", 1) + 1
            item["last_wrong_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_wrong_questions(wrong_list)
            return
    entry = question_to_dict(question)
    entry["wrong_count"] = 1
    entry["last_wrong_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    wrong_list.append(entry)
    save_wrong_questions(wrong_list)


def remove_from_wrong_book(question_text):
    """答对后从错题本移除。"""
    wrong_list = load_wrong_questions()
    wrong_list = [w for w in wrong_list if w["question"] != question_text]
    save_wrong_questions(wrong_list)


# ══════════════════════════════════════════════════════════════════════════════
#  历史记录管理
# ══════════════════════════════════════════════════════════════════════════════

def load_history():
    return load_json(HISTORY_FILE, [])


def save_history(history):
    save_json(HISTORY_FILE, history)


def add_history_record(count, difficulty_label, score, total, wrong_count, duration_seconds=0):
    history = load_history()
    record = {
        "id": int(time.time() * 1000),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "question_count": count,
        "difficulty": difficulty_label,
        "score": score,
        "total": total,
        "percent": round(score / total * 100, 1) if total > 0 else 0,
        "wrong_count": wrong_count,
        "duration_seconds": duration_seconds,
    }
    history.append(record)
    save_history(history)
    return record


# ══════════════════════════════════════════════════════════════════════════════
#  考试核心逻辑
# ══════════════════════════════════════════════════════════════════════════════

def ask_question(idx, total, q, is_review=False):
    """展示单题并获取用户答案。返回 (user_answer, quit_flag)。"""
    diff_label = {"easy": "简单", "medium": "中等", "hard": "困难"}.get(q["difficulty"], q["difficulty"])
    print("\n" + "-" * 56)
    tag = "【错题回顾】" if is_review else ""
    print(f"第 {idx}/{total} 题  {tag}[{diff_label}]")
    print(q["question"])
    for key in ("A", "B", "C", "D"):
        print(f"  {key}. {q['options'][key]}")

    while True:
        prompt = "你的答案（A/B/C/D，Q 提前交卷）："
        user_ans = input(prompt).strip().upper()
        if user_ans == "Q":
            return None, True
        if user_ans in ("A", "B", "C", "D"):
            return user_ans, False
        print("输入无效，请输入 A、B、C 或 D。")


def run_quiz(selected, is_review=False):
    """执行一轮答题，返回 (score, answered, wrong_questions_list, duration_seconds)。"""
    start_time = time.time()
    score = 0
    wrong_list = []
    total = len(selected)
    for idx, q in enumerate(selected, 1):
        user_ans, quit_flag = ask_question(idx, total, q, is_review)
        if quit_flag:
            print(f"\n提前交卷。当前得分：{score}/{idx - 1}")
            duration = int(time.time() - start_time)
            return score, idx - 1, wrong_list, duration

        if user_ans == q["answer"]:
            print("回答正确！")
            score += 1
            if is_review:
                remove_from_wrong_book(q["question"])
        else:
            print(f"回答错误。正确答案是 {q['answer']}：{q['options'][q['answer']]}")
            wrong_list.append(q)
            if not is_review:
                add_to_wrong_book(q)
    duration = int(time.time() - start_time)
    return score, total, wrong_list, duration


def show_result(score, total, duration=0):
    print("\n" + "=" * 56)
    print(f"考试完成！答对 {score}/{total} 题")
    if total > 0:
        percent = score / total * 100
        print(f"正确率：{percent:.1f}%")
        if percent >= 90:
            print("评级：优秀")
        elif percent >= 70:
            print("评级：良好")
        elif percent >= 60:
            print("评级：及格")
        else:
            print("评级：不及格，继续加油！")
    if duration >= 0:
        minutes = duration // 60
        seconds = duration % 60
        print(f"用时：{minutes}分{seconds}秒")
        if total > 0:
            avg = duration / total
            print(f"平均每题用时：{avg:.1f}秒")


# ══════════════════════════════════════════════════════════════════════════════
#  菜单与交互
# ══════════════════════════════════════════════════════════════════════════════

def get_version():
    """读取 VERSION 文件内容，失败则返回默认版本号。"""
    version_file = os.path.join(BASE_DIR, "VERSION")
    try:
        with open(version_file, "r", encoding="utf-8") as f:
            return f.read().strip()
    except (IOError, OSError):
        return "2.1.0"


def print_main_menu():
    version = get_version()
    print("\n" + "=" * 56)
    print(f"           Python 考试系统  v{version}")
    print("=" * 56)
    print("  1. 开始考试")
    print("  2. 错题回顾")
    print("  3. 历史记录")
    print("  0. 退出")


def choose_count(total_available):
    print(f"\n当前可用题目：{total_available} 道")
    print("请选择题量：")
    for i, n in enumerate(QUIZ_OPTIONS, 1):
        mark = "（题库不足）" if n > total_available else ""
        print(f"  {i}. {n} 道 {mark}")
    print("  0. 返回上一级")
    while True:
        c = input("请输入编号：").strip()
        if c == "0":
            return None
        if c.isdigit() and 1 <= int(c) <= len(QUIZ_OPTIONS):
            count = QUIZ_OPTIONS[int(c) - 1]
            if count > total_available:
                print(f"题库只有 {total_available} 道，无法选 {count} 道，请重选。")
                continue
            return count
        print("输入无效。")


def choose_difficulty():
    print("\n请选择难度：")
    for k, (_, label) in DIFFICULTY_LEVELS.items():
        print(f"  {k}. {label}")
    print("  0. 返回上一级")
    while True:
        c = input("请输入编号：").strip()
        if c == "0":
            return None
        if c in DIFFICULTY_LEVELS:
            return DIFFICULTY_LEVELS[c]
        print("输入无效。")


def mode_start_exam():
    diff_result = choose_difficulty()
    if diff_result is None:
        return
    diff_key, diff_label = diff_result
    all_questions = load_questions(QUESTIONS_DIR, diff_key)
    if not all_questions:
        print("该难度下没有题目。")
        return

    count = choose_count(len(all_questions))
    if count is None:
        return

    # 题库不足保护
    if count > len(all_questions):
        print(f"[提示] 需要 {count} 道题，但当前题库仅有 {len(all_questions)} 道，无法开始考试。")
        return None

    selected = random.sample(all_questions, count)
    print(f"\n开始考试！共 {count} 道题（{diff_label}），祝你好运。")
    score, answered, wrong_list, duration = run_quiz(selected, is_review=False)
    show_result(score, answered, duration)
    add_history_record(count, diff_label, score, answered, len(wrong_list), duration)
    print(f"本次错题 {len(wrong_list)} 道已自动加入错题本。")


def mode_review_wrong():
    wrong_list = load_wrong_questions()
    if not wrong_list:
        print("\n错题本为空，继续保持！")
        return
    print(f"\n错题本共有 {len(wrong_list)} 道题。")
    count = choose_count(len(wrong_list))
    if count is None:
        return
    selected = random.sample(wrong_list, count)
    # 转回统一格式
    selected = [dict(q) for q in selected]
    print(f"\n开始错题回顾！共 {count} 道题，答对后自动从错题本移除。")
    score, answered, _, duration = run_quiz(selected, is_review=True)
    show_result(score, answered, duration)


def mode_show_history():
    history = load_history()
    if not history:
        print("\n暂无考试记录。")
        return
    print("\n" + "=" * 64)
    print(f"{'序号':<4}{'日期':<20}{'难度':<8}{'题量':<6}{'得分':<8}{'正确率':<8}{'用时':<8}{'错题数'}")
    print("-" * 64)
    for idx, r in enumerate(history, 1):
        dur = r.get("duration_seconds", 0)
        if dur >= 60:
            dur_str = f"{dur//60}分{dur%60}秒"
        else:
            dur_str = f"{dur}秒"
        print(f"{idx:<4}{r['date']:<20}{r['difficulty']:<8}"
              f"{r['question_count']:<6}{r['score']}/{r['total']:<5}"
              f"{r['percent']}%{'':<3}{dur_str:<8}{r['wrong_count']}")
    print("=" * 64)
    # 统计
    if history:
        avg = sum(r["percent"] for r in history) / len(history)
        total_time = sum(r.get("duration_seconds", 0) for r in history)
        print(f"共考试 {len(history)} 次，平均正确率 {avg:.1f}%，累计用时 {total_time//60}分{total_time%60}秒")


# ══════════════════════════════════════════════════════════════════════════════
#  退出控制
# ══════════════════════════════════════════════════════════════════════════════

def wait_for_esc():
    print("\n" + "=" * 56)
    print("按 ESC 键关闭窗口...")
    try:
        import msvcrt
        while True:
            if msvcrt.kbhit():
                if msvcrt.getch() == b"\x1b":
                    break
    except ImportError:
        input("按回车键退出...")


def main():
    ensure_data_dir()
    while True:
        print_main_menu()
        choice = input("\n请选择操作（0-3）：").strip()
        if choice == "0":
            break
        elif choice == "1":
            mode_start_exam()
        elif choice == "2":
            mode_review_wrong()
        elif choice == "3":
            mode_show_history()
        else:
            print("输入无效，请输入 0-3。")
    wait_for_esc()


if __name__ == "__main__":
    main()
