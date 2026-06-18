# 算力事业部 · 招聘智能助手

> 从 HTML 原型到生产级 AI 招聘系统的 2 周冲刺。

## 🎯 项目目标

把 `算力招聘助手原型v2.html` 这个单文件原型，**2 周内**改造成：
- ✅ 多人可用的 Web 系统
- ✅ 5 大核心模块（解析 / 推荐 / 简历库 / 部门配置 / 用户管理）
- ✅ 真 AI 能力（简历解析 + 匹配 + 面试题 + 智能分流）
- ✅ 5 种角色权限
- ✅ PDF 上传
- ✅ Docker 部署

## 📂 项目结构

```
recruit-assistant/
├── backend/           # FastAPI 后端（Python）
│   ├── app/
│   ├── scripts/
│   └── README.md
├── frontend/          # React + Vite 前端（Day 3-7）
├── docs/              # 文档
└── README.md
```

## 🗓️ 2 周路线图

| Day | 目标 | 状态 |
|---|---|---|
| 1-2 | 后端骨架（FastAPI + PG + 5 表） | 🚧 进行中 |
| 3-4 | 5 大模块 API + JWT 鉴权 | ⏳ |
| 5-7 | 前端（React + Tailwind + shadcn） | ⏳ |
| 8-9 | AI 集成（Claude/DeepSeek API） | ⏳ |
| 10-11 | PDF 解析（PyMuPDF + LLM） | ⏳ |
| 12-13 | 测试 + 文档 + bug 修复 | ⏳ |
| 14 | Docker 部署 + 演示 | ⏳ |

## 🚀 快速开始

### 启动后端

```bash
cd backend
uv sync
cp .env.example .env  # 配 LLM API Key
createdb recruit_assistant
uv run python scripts/seed.py
uv run uvicorn app.main:app --reload --port 8000
```

API 文档：<http://localhost:8000/docs>

### 测试账号

| 工号 | 角色 | 密码 |
|---|---|---|
| A0001 | 管理员 | 123456 |
| D1001 | HRD | 123456 |
| H2087 | HRBP | 123456 |
| H3056 | HRBP | 123456 |
| S2001 | 社招负责人 | 123456 |
| X3001 | 校招负责人 | 123456 |

## 🛠️ 技术栈

**后端**：FastAPI · SQLAlchemy 2.0 · Alembic · PostgreSQL 17 + pgvector · Redis · JWT  
**AI**：Claude / DeepSeek / OpenAI（OpenAI 兼容协议）  
**PDF**：PyMuPDF  
**前端**（Day 3-7）：React 18 · Vite · Tailwind CSS · shadcn/ui  
**部署**（Day 14）：Docker · OrbStack

## 📋 5 大模块对应原 HTML

| 原型页面 | 后端 API | 权限 |
|---|---|---|
| 简历解析 | `/analysis/match` `/analysis/questions` | HRBP+ |
| 简历推荐 | `/analysis/route` `/resumes/recommend` | HRBP+ |
| 简历库 | `/resumes` | 按角色过滤 |
| 部门与岗位配置 | `/departments` `/positions` | HRD/HRBP |
| 用户管理 | `/users` | 管理员 |

## 📜 进度

详见 [docs/PROGRESS.md](docs/PROGRESS.md)