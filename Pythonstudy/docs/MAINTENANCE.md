# 维护与扩展指南

本文档面向项目维护者，说明日常维护、代码扩展、版本管理的规范。

---

## 一、日常维护

### 1.1 题库维护

| 操作 | 方法 | 频率建议 |
|---|---|---|
| 新增题目 | `add_questions.py` 或手动编辑 txt | 按需 |
| 检查格式 | `python add_questions.py stats` | 每次批量修改后 |
| 删除题目 | 直接编辑对应 txt 文件，删除该行 | 按需 |
| 修改答案 | 直接编辑对应 txt 文件 | 按需 |
| 按主题拆分 | 在 `questions/` 下新建 txt 文件 | 题库超过 100 道时 |

**注意**：修改题库后，`data/wrong_questions.json` 中已记录的错题不会自动同步。如果题目内容被修改，建议手动清理错题本中对应的旧题目。

### 1.2 数据维护

- `data/history.json`：考试历史，只增不改。如需重置，删除文件。
- `data/wrong_questions.json`：错题本，程序自动增删。如需清空，删除文件。
- 两个文件均为 UTF-8 JSON，可手动查看，但**不建议手动编辑**。

### 1.3 定期检查清单

- [ ] 运行 `python add_questions.py stats` 确认题库数量正常
- [ ] 运行 `python main.py` 抽 3 道题验证流程
- [ ] 检查 `data/` 目录文件是否异常增大
- [ ] 确认所有题库文件编码为 UTF-8

---

## 二、代码结构说明

### 2.1 main.py 模块划分

```
main.py
├── 路径与常量配置        (BASE_DIR, QUIZ_OPTIONS, DIFFICULTY_LEVELS)
├── 数据持久化层          (load_json, save_json, ensure_data_dir)
├── 题库加载              (load_questions, question_to_dict)
├── 错题本管理            (load/save/add/remove_wrong_questions)
├── 历史记录管理          (load/save/add_history_record)
├── 考试核心逻辑          (ask_question, run_quiz, show_result)
├── 菜单与交互            (print_main_menu, mode_*, choose_*)
├── 退出控制              (wait_for_esc)
└── 入口                  (main)
```

### 2.2 add_questions.py 模块划分

```
add_questions.py
├── 配置与工具            (BASE_DIR, DIFFICULTIES, ensure_dir, list_files)
├── 格式校验              (validate_line)
├── 单条添加              (add_single)
├── 批量导入              (batch_import)
├── 统计查看              (show_stats)
├── 目标选择              (select_target)
├── 交互菜单              (interactive_menu)
└── 入口                  (main)
```

---

## 三、常见扩展点

### 3.1 修改可选题目数量

编辑 `main.py` 中的 `QUIZ_OPTIONS`：

```python
QUIZ_OPTIONS = [3, 5, 20, 50, 100]  # 按需增减
```

同时 `add_questions.py` 中无此题量配置，无需同步修改。

### 3.2 增加难度档位

1. `main.py` 中修改 `DIFFICULTY_LEVELS`：
   ```python
   DIFFICULTY_LEVELS = {
       "1": ("all", "全部难度"),
       "2": ("easy", "简单"),
       "3": ("medium", "中等"),
       "4": ("hard", "困难"),
       # 新增：
       "5": ("expert", "专家"),
   }
   ```
2. `add_questions.py` 中修改 `DIFFICULTIES` 和 `DIFF_LABELS`
3. `validate_line` 中增加新难度的校验
4. 题库文件中使用新难度值
5. `ask_question` 中的难度标签映射需同步更新

### 3.3 增加新题型（如多选题、判断题）

当前系统仅支持单选题。扩展新题型需要：

1. 题库格式增加题型字段（如第 8 字段：`single`/`multi`/`judge`）
2. `load_questions` 解析题型
3. `ask_question` 根据题型展示不同交互
4. `run_quiz` 判分逻辑适配
5. 错题本和历史记录结构同步更新

> 建议：如需要多题型，建议新建 `main_v3.py` 而非直接改 v2.0，保持版本清晰。

### 3.4 增加考试计时功能

在 `run_quiz` 中用 `time.time()` 记录开始和结束时间，结果存入 `add_history_record`，并在 `show_result` 中展示。

### 3.5 导出成绩报告

读取 `data/history.json`，用 `json` + 字符串格式化生成 txt 或 html 报告。可新建 `export_report.py`。

---

## 四、版本管理规范

### 4.1 版本号

采用**语义化版本**（Semantic Versioning）：

```
主版本号.次版本号.修订号
  │       │       │
  │       │       └─ 向下兼容的问题修复
  │       └───────── 向下兼容的功能新增
  └───────────────── 不兼容的架构改动
```

版本号同时记录在两处：
- `VERSION` 文件（纯文本，仅一行）
- `docs/CHANGELOG.md`（变更详情）

### 4.2 发布流程

1. 修改代码并测试
2. 更新 `VERSION` 文件
3. 在 `docs/CHANGELOG.md` 顶部添加新版本条目
4. 更新 `docs/README.md` 中的版本号和日期
5. Git 提交并打 tag：
   ```bash
   git add -A
   git commit -m "release: v2.0.0"
   git tag v2.0.0
   git push --tags
   ```

### 4.3 Git 提交信息规范

采用 Conventional Commits 格式：

```
<类型>: <简短描述>

类型：
  feat     新功能
  fix      修复 bug
  docs     文档变更
  style    格式调整（不影响代码逻辑）
  refactor 重构（既不新增功能也不修 bug）
  test     测试相关
  chore    构建/工具/依赖相关
```

示例：
```
feat: 新增错题回顾功能
fix: 修复题库不足时崩溃的问题
docs: 更新题库格式规范
```

---

## 五、备份策略

| 数据 | 重要性 | 备份方式 |
|---|---|---|
| `questions/` | 高（核心内容） | Git 版本控制 + 定期导出 |
| `data/history.json` | 中 | Git 跟踪或定期复制 |
| `data/wrong_questions.json` | 低 | 可重新积累，可选备份 |
| 代码文件 | 高 | Git 版本控制 |
| `docs/` | 中 | Git 版本控制 |

**最小备份方案**：将整个项目初始化为 Git 仓库并推送到 GitHub/Gitee。

---

## 六、故障排查

| 现象 | 可能原因 | 解决方法 |
|---|---|---|
| 题库加载 0 道 | questions 目录为空或格式全错 | 运行 stats 检查，确认格式 |
| 中文乱码 | 文件编码不是 UTF-8 | 用编辑器转存为 UTF-8 |
| 历史记录不保存 | data 目录无写权限 | 检查目录权限，或以管理员运行 |
| ESC 无反应 | 非 Windows 平台 | 正常，按回车键退出 |
| 批量导入全跳过 | 源文件格式不对（缺难度字段） | 对照 QUESTION_FORMAT.md 检查 |
| 程序启动报错 | Python 版本过低 | 升级到 3.8+ |
