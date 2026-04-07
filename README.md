# Jira AI Analyzer (Python + Company AI API + Qt UI)

一个可运行的完整示例（实时读取 Jira，不做本地历史导入）：

- 对指定 issue 进行实时分析
- 分析时实时从 Jira 拉取最近历史问题作为候选
- 同时支持两个 Jira：
  - `https://jira.n.xiaomi.com`
  - `https://jira-phone.mioffice.cn`
- 基于公司 AI Embedding API 做相似问题检索
- 基于公司 AI Analysis API 生成结构化分析报告
- 提供 FastAPI 后端 + PySide6(Qt) 桌面 UI

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
- `BACKEND_URL`：Qt UI 连接后端地址（默认 `http://127.0.0.1:8000`）

## 3. 启动后端

```bash
uvicorn backend.main:app --reload --port 8000
```

## 4. 启动 Qt UI

Qt UI 不再要求手动输入后端地址，会直接读取 `.env` 中的 `BACKEND_URL`（默认 `http://127.0.0.1:8000`）。

```bash
python qt_ui/main.py
```

## 5. 可用接口

- `POST /analyze/{issue_key}`：实时拉取 issue 并分析
- `POST /webhook/jira`：接收 Jira webhook 后触发分析
- `GET /report/{issue_key}`：查看已保存报告

## 6. 处理流程

1. 实时读取当前 issue（优先在两个 Jira 中顺序查找）。
2. 从两个 Jira 拉取最近 `CANDIDATE_POOL_SIZE` 条历史 issue（排除当前 issue）。
3. 用 embedding 计算相似度，取前 `TOP_K` 作为上下文。
4. 调用分析接口输出结构化 JSON。
5. 保存报告到本地 SQLite（只保存报告，不保存历史库）。
