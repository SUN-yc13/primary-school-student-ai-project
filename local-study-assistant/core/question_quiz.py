import random

quiz_list = [
    {"question": "《静夜思》作者是谁？", "answer": "李白"},
    {"question": "圆周率大约是多少？", "answer": "3.1415926"},
    {"question": "少壮不努力的下一句？", "answer": "老大徒伤悲"}
]

def start_quiz():
    score = 0
    random.shuffle(quiz_list)
    for item in quiz_list:
        ans = input(item["question"] + "\n你的答案：")
        if ans == item["answer"]:
            print("答对啦！")
            score += 1
        else:
            print(f"答错，正确答案：{item['answer']}")
    total = len(quiz_list)
    print(f"本次得分：{score}/{total}")
    return score, total