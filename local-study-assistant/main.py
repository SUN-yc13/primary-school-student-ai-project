from core.nlp_match import match_answer, knowledge
from core.essay_generator import build_article
from core.question_quiz import start_quiz
import os

def clear_screen():
    os.system("cls")

# 文件路径配置
folder_path = "user_data"
file_path = os.path.join(folder_path, "history.txt")
score_file = os.path.join(folder_path, "score.txt")

# 自动创建文件夹
if not os.path.exists(folder_path):
    os.mkdir(folder_path)

def menu():
    print("====== 离线学习助手 V2.0 ======")
    print("1. 连续智能对话")
    print("2. 自动生成小升初作文")
    print("3. 知识刷题自测")
    print("4. 查看历史聊天记录")
    print("5. 查看刷题成绩单")
    print("6. 退出软件")
    return input("请输入序号：")

if __name__ == "__main__":
    while True:
        option = menu()
        if option == "1":
            print("\n====开启连续对话，输入exit结束聊天====")
            chat_history = []
            while True:
                question = input("你：")
                if "exit" in question.lower():
                    break
                reply = match_answer(question, knowledge)
                chat_history.append(f"你：{question}")
                chat_history.append(f"助手：{reply}")
                print(f"助手：{reply}")

            # 保存聊天记录
            with open(file_path, "a", encoding="utf-8") as f:
                for line in chat_history:
                    f.write(line + "\n")
                f.write("-" * 30 + "\n")

            input("\n按下回车键清屏返回菜单")
            clear_screen()

        elif option == "2":
            print("\n====作文自动生成器====")
            article = build_article()
            print("生成短文：")
            print(article)
            input("\n按下回车键返回菜单")
            clear_screen()

        elif option == "3":
            print("\n====开始答题测试====")
            score, total = start_quiz()
            # 保存本次成绩
            with open(score_file, "a", encoding="utf-8") as f:
                f.write(f"本次成绩：{score}/{total}\n")
            input("\n答题结束，回车返回菜单")
            clear_screen()

        elif option == "4":
            print("\n====历史聊天记录====")
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    print(content)
            else:
                print("暂无历史记录")
            input("\n回车返回菜单")
            clear_screen()

        elif option == "5":
            print("\n====历次刷题成绩====")
            if os.path.exists(score_file):
                with open(score_file, "r", encoding="utf-8") as f:
                    print(f.read())
            else:
                print("暂无成绩记录")
            input("回车返回菜单")
            clear_screen()

        elif option == "6":
            print("程序结束")
            break
