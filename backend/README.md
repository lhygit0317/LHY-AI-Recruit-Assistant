# 算力事业部 · 招聘智能助手 (Backend)

FastAPI + PostgreSQL + AI 简历分析。

## 🚀 启动

```bash
# 1. 装依赖
uv sync

# 2. 配 .env（从 .env.example 复制）
cp .env.example .env
# 编辑 .env，至少配一个 LLM 的 API Key

# 3. 创建数据库（PostgreSQL 17）
createdb recruit_assistant

# 4. 建表 + 写种子数据
uv run python scripts/seed.py

# 5. 启动服务
uv run uvicorn app.main:app --reload --port 8000
```

打开 http://localhost:8000/docs 看 API 文档。

## 🔐 测试账号（密码统一 `123456`）

| 工号 | 角色 | 姓名 |
|---|---|---|
| A0001 | 管理员 | 管理员 |
| D1001 | HRD | 周明 |
| H2087 | HRBP | 张敏 |
| H3056 | HRBP | 郑燕 |
| S2001 | 社招负责人 | 孙磊 |
| X3001 | 校招负责人 | 陈晨 |

## 📂 项目结构

```
backend/
├── app/
│   ├── api/        # 路由
│   │   ├── v1/    # v1 业务路由
│   │   ├── deps.py # 依赖注入（鉴权）
│   │   └── router.py
│   ├── core/       # 核心：配置、鉴权
│   ├── db/         # 数据库连接
│   ├── models/     # ORM 模型（5 张核心表）
│   ├── schemas/    # Pydantic 请求/响应模型
│   ├── services/   # 业务服务（LLM、PDF 解析）
│   ├── utils/
│   └── main.py     # FastAPI 入口
├── scripts/
│   └── seed.py     # 种子数据
├── pyproject.toml
├── .env.example
└── README.md
```

## 🗄️ 5 张核心表

- `users` — 用户（含角色）
- `departments` — 部门（含 HRBP / 主管 / 锻炼干部）
- `positions` — 岗位 JD（含关键词 + 隐性标签权重）
- `resumes` — 简历（含结构化字段）
- `notifications` — 通知

## 🛣️ 5 大模块 API

| 模块 | 前缀 | 权限 |
|---|---|---|
| 认证 | `/api/v1/auth` | 公开/已登录 |
| 用户管理 | `/api/v1/users` | 管理员可写，其他人只读 |
| 部门 | `/api/v1/departments` | 关系表全员可见，写需有权限 |
| 岗位 | `/api/v1/positions` | 同上，HRBP 可配隐性标签 |
| 简历 | `/api/v1/resumes` | 按角色过滤可见范围 |
| AI 分析 | `/api/v1/analysis` | 匹配分析 + 面试题 + 智能分流 |