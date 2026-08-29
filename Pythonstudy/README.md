# Python 考试系统

> 一个轻量、可扩展的 Python 知识单选题考试与练习系统。

- **版本**：2.0.0
- **更新日期**：2026-08-29
- **Python 要求**：3.8+（开发环境 3.13）
- **平台**：Windows（ESC 退出）/ 跨平台（自动降级为回车退出）

---

## 目录

- [功能特性](#功能特性)
- [快速开始](#快速开始)
- [目录结构](#目录结构)
- [题库格式](#题库格式)
- [增加题目](#增加题目)
- [数据文件说明](#数据文件说明)
- [维护与扩展](#维护与扩展)
- [版本历史](#版本历史)
- [常见问题](#常见问题)

---

## 功能特性

| 功能 | 说明 |
|---|---|
| 随机考试 | 支持 3 / 5 / 20 / 50 / 100 道题，从题库随机抽取 |
| 难度筛选 | 全部 / 简单 / 中等 / 困难 四档可选 |
| 错题本 | 答错的题自动收录，累计错误次数与最近错误时间 |
| 错题回顾 | 从错题本抽题重做，答对后自动移出错题本 |
| 历史记录 | 每次考试自动保存日期、难度、题量、得分、正确率、错题数 |
| 题目管理 | 交互式单条添加 / 文件批量导入 / 题库统计 |
| 防闪退 | 程序结束后窗口保持，按 **ESC** 键才关闭 |

---

## 快速开始

### 1. 环境检查

```bash
python --version
# 需输出 Python 3.8 及以上版本
```

### 2. 启动考试

```bash
python main.py
```

或在文件管理器中**双击 `main.py`**。

### 3. 操作流程

1. 主菜单选择 `1. 开始考试`
2. 选择难度（全部 / 简单 / 中等 / 困难）
3. 选择题量（3 / 5 / 20 / 50 / 100）
4. 逐题输入 `A/B/C/D` 作答，输入 `Q` 提前交卷
5. 查看成绩与正确率
6. 按 `ESC` 关闭窗口

### 4. 管理题目

```bash
python add_questions.py          # 交互菜单
python add_questions.py stats    # 查看题库统计
python add_questions.py import 新题.txt python_easy   # 批量导入
```

---

## 目录结构

```
Pythonstudy/
├── main.py                  # 主程序（考试入口）
├── add_questions.py         # 题目管理工具
├── questions/               # 题库目录（所有 .txt 题库放这里）
│   ├── python_easy.txt      # 简单题（30 道）
│   ├── python_medium.txt    # 中等题（30 道）
│   └── python_hard.txt      # 困难题（30 道）
├── data/                    # 运行数据（自动生成，无需手动编辑）
│   ├── history.json         # 考试历史记录
│   └── wrong_questions.json # 错题本
├── docs/                    # 文档目录
│   ├── QUESTION_FORMAT.md   # 题库格式详细规范
│   ├── MAINTENANCE.md       # 维护与扩展指南
│   └── CHANGELOG.md         # 版本变更日志
├── VERSION                  # 版本号（纯文本，一行）
└── .gitignore               # Git 忽略规则
```

---

## 题库格式

题库为 UTF-8 编码的纯文本文件，**每行一道题**，7 个字段用竖线 `|` 分隔：

```
难度|题目内容|选项A|选项B|选项C|选项D|正确答案
```

### 字段说明

| 位置 | 字段 | 取值 | 说明 |
|---|---|---|---|
| 1 | 难度 | `easy` / `medium` / `hard` | 必须小写 |
| 2 | 题目 | 任意文本 | 不能为空 |
| 3-6 | 选项 A-D | 任意文本 | 四个选项 |
| 7 | 正确答案 | `A` / `B` / `C` / `D` | 大小写均可，自动转大写 |

### 示例

```
easy|Python 中定义函数用哪个关键字？|function|def|func|define|B
medium|列表推导式 [x*2 for x in range(3)] 的结果是？|[0,1,2]|[0,2,4]|[2,4,6]|报错|B
hard|Python 中 GIL 的主要影响是？|多进程无法并行|多线程CPU密集型无法真正并行|单线程变慢|内存泄漏|B
```

### 规则

- 以 `#` 开头的行为**注释**，空行会被忽略
- 一行必须恰好 **7 个字段**，否则程序警告并跳过
- `questions/` 目录下可放**多个** `.txt` 文件，主程序自动合并
- 保存编码必须为 **UTF-8**，否则中文乱码

> 详细规范见 [docs/QUESTION_FORMAT.md](docs/QUESTION_FORMAT.md)

---

## 增加题目

### 方式一：交互式添加（推荐新手）

```bash
python add_questions.py
```

选择 `1. 单条添加题目` → 选择目标题库 → 按提示输入难度、题目、四个选项、答案。

### 方式二：批量导入（推荐大量题目）

1. 准备一个 txt 文件，每行按格式写好题目
2. 执行：
   ```bash
   python add_questions.py import D:\新题.txt python_medium
   ```
3. 程序自动校验格式，合法题目追加，错误行提示并跳过

### 方式三：手动编辑

用 VS Code / 记事本（选 UTF-8 编码）直接打开 `questions/` 下的 txt 文件，在末尾追加。

### 方式四：新建题库文件

在 `questions/` 下新建 `.txt` 文件，首行写注释，后续按格式写题。主程序自动识别，**无需改代码**。

---

## 数据文件说明

程序运行后会在 `data/` 目录自动生成两个 JSON 文件：

### history.json — 考试历史

```json
[
  {
    "id": 1,
    "date": "2026-08-29 20:00:00",
    "question_count": 5,
    "difficulty": "全部难度",
    "score": 4,
    "total": 5,
    "percent": 80.0,
    "wrong_count": 1
  }
]
```

### wrong_questions.json — 错题本

```json
[
  {
    "difficulty": "medium",
    "question": "列表推导式 [x*2 for x in range(3)] 的结果是？",
    "options": {"A": "[0,1,2]", "B": "[0,2,4]", "C": "[2,4,6]", "D": "报错"},
    "answer": "B",
    "source": "python_medium.txt",
    "wrong_count": 2,
    "last_wrong_date": "2026-08-29 20:05:00"
  }
]
```

> 这两个文件是程序自动管理的，**一般不需要手动编辑**。如需重置，删除对应文件即可。

---

## 维护与扩展

详见 [docs/MAINTENANCE.md](docs/MAINTENANCE.md)，要点：

- **题库维护**：按主题/难度分文件，定期校验格式
- **代码扩展**：题量选项改 `QUIZ_OPTIONS`，难度档位改 `DIFFICULTY_LEVELS`
- **版本管理**：语义化版本 + Git 提交规范
- **备份**：`questions/` 和 `data/` 是核心数据，建议定期备份或接入 Git

---

## 版本历史

| 版本 | 日期 | 主要变更 |
|---|---|---|
| v2.0.0 | 2026-08-29 | 难度分级题库、错题本、历史记录、专业文档体系、题库扩充至 90 道 |
| v1.0.0 | 2026-08-29 | 初始版本，基础随机考试功能 |

完整变更日志见 [docs/CHANGELOG.md](docs/CHANGELOG.md)

---

## 常见问题

**Q：双击 main.py 窗口一闪而过？**
A：请在命令行运行 `python main.py`，或确认 Python 已加入 PATH。正常结束后会等待 ESC，不会闪退。

**Q：中文乱码？**
A：确保题库文件保存为 UTF-8 编码。Windows 记事本保存时在编码下拉框选「UTF-8」。

**Q：提示题库不足？**
A：当前题库总量不够所选数量，换小题量或用 `add_questions.py` 补充题目。

**Q：如何清空错题本/历史记录？**
A：删除 `data/wrong_questions.json` 或 `data/history.json`，程序会重新生成空文件。

**Q：可以在 Mac/Linux 运行吗？**
A：可以。ESC 监听会自动降级为「按回车键退出」，其余功能完全一致。

---

## 许可证

本项目仅供学习与内部使用。
