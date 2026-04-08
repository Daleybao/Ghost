# Jira AI Analyzer（纯 Qt 本地版）

这是一个**不需要后端服务**的本地工具：

- 直接在 Qt 客户端里实时读取 Jira
- 同时支持两个 Jira：
  - `https://jira.n.xiaomi.com`
  - `https://jira-phone.mioffice.cn`
- 调用公司 AI Embedding / Analysis API
- 本地 SQLite 保存分析报告

## 1. 安装

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2. 配置 `.env`

- `AI_EMBEDDING_URL`：公司 embedding 接口地址
- `AI_ANALYSIS_URL`：公司分析接口地址
- `AI_API_KEY`：公司 AI 接口密钥（如有）
- `AI_MODEL`：模型名（如接口需要）
- `JIRA_BASE_URL`：旧 Jira 地址（默认 `https://jira.n.xiaomi.com`）
- `NEW_JIRA_BASE_URL`：新 Jira 地址（默认 `https://jira-phone.mioffice.cn`）
- `JIRA_API_TOKEN`：Jira 访问令牌（Bearer）
- `DB_PATH`：本地 SQLite 路径
- `CANDIDATE_POOL_SIZE`：候选 issue 数
- `TOP_K`：相似 issue 取前 K

## 3. 启动（仅 Qt）

```bash
python qt_ui/main.py
```

## 4. 运行流程

1. 输入 issue key。
2. Qt 直接请求 Jira 获取当前 issue + 候选历史 issue。
3. 本地计算相似度并调用 AI 生成分析。
4. 报告写入本地 SQLite，可直接查询。
