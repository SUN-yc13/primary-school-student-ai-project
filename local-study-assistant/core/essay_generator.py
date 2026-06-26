import random

begin = [
    "在我的童年里，发生过许多小事。",
    "直到现在，我依然记得那件往事。",
    "成长路上，总有难忘的回忆。"
]
middle = [
    "一开始我手足无措，屡屡碰壁。",
    "我没有放弃，静下心反复练习。",
    "在别人的鼓励下，我重新鼓起勇气。"
]
ending = [
    "这件事让我懂得坚持就是胜利。",
    "这次经历，让我收获了成长。",
    "这件小事，我永远不会忘记。"
]

def build_article():
    p1 = random.choice(begin)
    p2 = random.choice(middle)
    p3 = random.choice(ending)
    full_text = p1 + p2 + p3
    return full_text