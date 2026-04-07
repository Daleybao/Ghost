# Jira AI Analyzer（纯 Qt 本地版）

一个可运行的本地工具（**无后端服务**）：

- 在 Qt 客户端里直接读取 Jira 并分析 issue
- 同时支持两个 Jira：
  - `https://jira.n.xiaomi.com`
  - `https://jira-phone.mioffice.cn`
- 基于公司 AI Embedding API 做相似问题检索
- 基于公司 AI Analysis API 生成结构化分析报告
- 报告保存到本地 SQLite（`DB_PATH`）

## 1. 安装

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2. 配置

项目已提供可直接编辑的 `.env` 文件。

必填环境变量：

- `AI_EMBEDDING_URL`：公司 embedding 接口地址
- `AI_ANALYSIS_URL`：公司分析接口地址
- `AI_API_KEY`：公司 AI 接口密钥（如有）
- `AI_MODEL`：模型名（如接口需要）
- `JIRA_BASE_URL`：旧 Jira 地址（默认 `https://jira.n.xiaomi.com`）
- `NEW_JIRA_BASE_URL`：新 Jira 地址（默认 `https://jira-phone.mioffice.cn`）
- `JIRA_API_TOKEN`：Jira 访问令牌（Bearer）

## 3. 启动（仅 Qt）

```bash
python qt_ui/main.py
```

## 4. 使用方式

1. 输入 Issue Key（如 `OPS-123`）
2. 点击“实时分析Issue”
3. 工具会本地执行：
   - 拉取当前 issue
   - 拉取候选历史 issue（`CANDIDATE_POOL_SIZE`）
   - embedding 相似度排序（`TOP_K`）
   - 调用 AI 生成报告
   - 存储到本地 SQLite
4. 点击“查询本地报告”可读取已存结果
