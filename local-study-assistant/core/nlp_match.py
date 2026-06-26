def match_answer(input_text, knowledge_lib):
    text = input_text.lower()
    for info in knowledge_lib:
        if info["keyword"] in text:
            return info["reply"]
    return "我暂时无法解答这个问题，请换一个问题。"

knowledge = [
    {"keyword": "静夜思 作者", "reply": "李白，唐代大诗人。"},
    {"keyword": "圆周率", "reply": "π≈3.1415926"},
    {"keyword": "小升初作文方法", "reply": "开头点题，中间详细叙事，结尾升华主旨。"}
]