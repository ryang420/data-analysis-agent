# 项目结构说明

本项目可在**本地**运行，无额外平台依赖。

## 目录结构

```
data-analysis-agent/
├── backend/           # 后端 (Python FastAPI + LangGraph Agent)
│   ├── src/
│   ├── config/
│   ├── scripts/
│   ├── assets/
│   └── requirements.txt
├── frontend/          # 前端 (Vite + React 聊天 UI)
│   ├── src/
│   └── package.json
├── .env.example
└── README.md
```

## 环境准备

1. 复制环境变量示例并填写（放在项目根目录或 backend/）：
   ```bash
   cp .env.example .env
   # 编辑 .env，至少设置 PGDATABASE_URL 和 OPENAI_API_KEY
   ```

2. 安装后端依赖（建议使用虚拟环境）：
   ```bash
   cd backend && pip install -r requirements.txt
   # 或
   bash backend/scripts/setup.sh
   ```

3. 准备数据库：创建 PostgreSQL 数据库，执行建表，然后导入 CSV：
   ```bash
   psql -h localhost -U user -d db -f backend/scripts/create_sales_data_table.sql
   PYTHONPATH=backend/src python backend/scripts/import_csv_to_db.py
   ```

## 本地运行

### 加载环境变量（可选）
```bash
source backend/scripts/load_env.sh
# 或
eval $(python backend/scripts/load_env.py)
```

### 运行流程（单次调用）
```bash
bash backend/scripts/local_run.sh -m flow -i '{"text": "分析本月销售趋势"}'
# 或
cd backend && PYTHONPATH=src python src/main.py -m flow -i '{"text": "你好"}'
```

### 启动 HTTP 服务（推荐本地调试）
```bash
bash backend/scripts/http_run.sh -p 8000
# 或省略 -p，默认 8000（避免 macOS AirPlay 占用 5000）
bash backend/scripts/http_run.sh
```
然后可调用：
- `POST /run` — 同步执行
- `POST /stream_run` — 流式执行（SSE）
- `POST /v1/chat/completions` — OpenAI 兼容接口（前端聊天推荐）

### 运行节点（仅 workflow 模式）
```bash
bash backend/scripts/local_run.sh -m node -n node_name
```

### 启动前端聊天 UI
```bash
# 1. 先启动后端（默认 8000 端口）
bash backend/scripts/http_run.sh

# 2. 启动前端
cd frontend && npm install && npm run dev
```
前端默认在 [http://localhost:5173](http://localhost:5173)，通过 Vite 代理访问后端 [http://localhost:8000](http://localhost:8000)。

**遇到 500 错误时**：查看后端终端日志获取详细堆栈；前端会显示错误信息。常见原因：`PGDATABASE_URL` 或 `OPENAI_API_KEY` 未配置、数据库连接失败。

## 环境变量说明（.env）

| 变量 | 说明 |
|------|------|
| `PGDATABASE_URL` | PostgreSQL 连接串（必填，Agent 工具与对话记忆会用） |
| `OPENAI_API_KEY` | OpenAI 或兼容 API 的 Key（必填） |
| `OPENAI_BASE_URL` | 可选，兼容 API 的 base URL |
| `PROJECT_ROOT` | 可选，指向 backend 目录，不设则脚本自动推断 |

详见 `.env.example`。

## 云端部署平台：
- 前端：Cloudflare Pages
- 后端：Fly.io (Docker)
- 数据库：Supabase