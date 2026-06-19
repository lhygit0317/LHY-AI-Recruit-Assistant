# Frontend - 算力事业部招聘智能助手

React 18 + Vite + TypeScript + Tailwind CSS + Zustand

## 🚀 启动

```bash
# 1. 装依赖
pnpm install   # 或 npm install

# 2. 启动 dev server
pnpm dev
# → http://localhost:5173
```

> 注意：需要先启动后端（http://localhost:8000），前端通过 Vite 代理转发 `/api/*` 请求。

## 📂 结构

```
src/
├── api/         # API client + 类型
├── components/  # 通用组件（Layout）
├── pages/       # 5 个核心页面
│   ├── Login.tsx       登录
│   ├── Resumes.tsx     简历库
│   ├── Parse.tsx       简历解析
│   ├── Recommend.tsx   简历推荐
│   ├── Positions.tsx   部门与岗位配置
│   └── Users.tsx       用户管理
├── store/       # Zustand 状态
├── lib/         # 工具
├── App.tsx      # 路由
└── main.tsx     # 入口
```

## 🎨 风格

参考原 `算力招聘助手原型v2.html` 的视觉风格：
- 浅蓝灰底 + 蓝/青/紫/橙多色 tag
- 卡片式布局
- 圆角 10-14px
- Space Grotesk 字体
- 中文用 PingFang SC / Microsoft YaHei

## 🛠 技术栈

- **React 18** + **TypeScript**
- **Vite 5** — 构建
- **Tailwind CSS 3** — 样式
- **React Router 6** — 路由
- **Zustand** — 状态管理
- **Axios** — HTTP
- **Lucide React** — 图标
- **React Hot Toast** — 通知

## 🔐 演示账号

| 工号 | 角色 | 密码 |
|---|---|---|
| A0001 | 管理员 | 123456 |
| D1001 | HRD | 123456 |
| H2087 | HRBP | 123456 |
| H3056 | HRBP | 123456 |
| S2001 | 社招负责人 | 123456 |
| X3001 | 校招负责人 | 123456 |