# 数据模型与数据库设计

## 1. 范围

本版覆盖 `TODO.md` 3.3 所要求的 V1 核心表：

- 用户、角色、用户角色关联
- 老人与子女绑定关系
- 风险告警
- 短信识别记录
- 通话识别记录
- 通知记录
- 工单与工单处置记录
- 风险规则、风险词库、提示模板
- 宣教内容

## 2. 模型分层

- `app/models/user.py`
  - `users`
  - `roles`
  - `user_role_links`
- `app/models/binding.py`
  - `elder_family_bindings`
- `app/models/risk.py`
  - `risk_alerts`
  - `sms_recognition_records`
  - `call_recognition_records`
- `app/models/notification.py`
  - `notification_records`
- `app/models/workorder.py`
  - `workorders`
  - `workorder_actions`
- `app/models/content.py`
  - `risk_rules`
  - `risk_lexicon_terms`
  - `prompt_templates`
  - `education_contents`

## 3. 关键关系

- 一个用户可拥有多个角色，通过 `user_role_links` 关联。
- 一个老人可绑定多个子女或亲属，通过 `elder_family_bindings` 管理授权状态与紧急联系人标记。
- 一条风险告警归属一个老人，可由短信或通话识别记录触发。
- 一条风险告警可扩散为多条通知记录，并在高风险场景下生成社区工单。
- 一个工单可记录多次状态流转和处置动作，通过 `workorder_actions` 留痕。

## 4. 字段设计原则

- 主键统一使用 `String(36)` UUID，方便前后端联调和离线样例数据准备。
- `created_at`、`updated_at` 统一下沉到公共 mixin。
- 状态、风险等级、渠道等先使用字符串字段保存，后续按业务成熟度再补充字典表或枚举约束。
- 识别记录、建议动作、命中规则等保留文本字段，兼容规则版输出与后续模型版输出。

## 5. 迁移机制

- Alembic 配置文件：`apps/backend-fastapi/alembic.ini`
- Alembic 环境入口：`apps/backend-fastapi/alembic/env.py`
- 首个初始化迁移：`apps/backend-fastapi/alembic/versions/20260414_0001_init_core_schema.py`

执行方式：

```bash
cd apps/backend-fastapi
.venv/bin/alembic upgrade head
```

前提：

- `APP_DATABASE_URL` 指向可连接的 PostgreSQL 实例
- 本地已安装项目依赖：`.venv/bin/pip install -e ".[dev]"`
