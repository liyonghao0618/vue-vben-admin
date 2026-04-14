# 后端基础工程

`apps/backend-fastapi` 是“守护桑榆”项目的 `FastAPI` 后端基础工程，目标是先完成 V1 所需的后端底座能力：

- 环境配置管理：开发、测试、生产
- 统一响应结构与异常处理
- 请求日志、中间件、健康检查
- JWT 鉴权与角色权限依赖
- OpenAPI 文档与接口目录草案
- SQLAlchemy 数据模型与 Alembic 迁移底座

## 快速启动

```bash
cd apps/backend-fastapi
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

启动后可访问：

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/redoc`
- `http://127.0.0.1:8000/api/v1/health`

## 默认演示账号

当前为基础工程阶段，内置演示账号用于验证鉴权与角色权限：

- `elder_demo / Elder123!`
- `family_demo / Family123!`
- `community_demo / Community123!`
- `admin_demo / Admin123!`

## 目录结构

```text
apps/backend-fastapi
├── app
│   ├── api
│   ├── constants
│   ├── core
│   ├── db
│   ├── models
│   ├── schemas
│   └── services
├── alembic
├── docs
├── .env.example
├── alembic.ini
└── pyproject.toml
```

## 数据库迁移

```bash
cd apps/backend-fastapi
.venv/bin/pip install -e ".[dev]"
.venv/bin/alembic upgrade head
```

默认通过 `APP_DATABASE_URL` 连接 PostgreSQL。首版已补齐 3.3 所需核心表结构，详见 [docs/database-design.md](/workspaces/vue-vben-admin/apps/backend-fastapi/docs/database-design.md)。
