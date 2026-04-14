# 接口目录与文档草案

## 1. 认证与权限

- `POST /api/v1/auth/login`：账号登录，返回 JWT
- `POST /api/v1/auth/logout`：退出登录，后续接入 token 黑名单或刷新策略
- `POST /api/v1/auth/refresh`：刷新 access token
- `GET /api/v1/auth/me`：获取当前用户信息
- `GET /api/v1/auth/admin-permissions`：管理员权限校验示例接口

## 2. 业务域接口规划

- `GET /api/v1/bindings`：查询老人与亲属绑定关系
- `POST /api/v1/bindings`：新增绑定
- `DELETE /api/v1/bindings/{binding_id}`：解绑
- `GET /api/v1/risk-alerts`：风险告警列表
- `GET /api/v1/risk-alerts/{alert_id}`：风险告警详情
- `GET /api/v1/notifications`：通知记录列表
- `PATCH /api/v1/notifications/{notification_id}/read`：通知标记已读
- `GET /api/v1/workorders`：社区工单列表
- `GET /api/v1/workorders/{workorder_id}`：社区工单详情
- `POST /api/v1/workorders/{workorder_id}/transition`：工单状态流转
- `GET /api/v1/admin/users`：管理端用户管理
- `GET /api/v1/admin/roles`：管理端角色权限
- `GET /api/v1/admin/rules`：管理端风险规则
- `GET /api/v1/admin/templates`：提示模板与内容管理
- `GET /api/v1/admin/system-config`：系统配置

## 3. 统一响应约定

```json
{
  "code": 0,
  "message": "ok",
  "data": {},
  "meta": {
    "request_id": "trace-id",
    "timestamp": 1710000000000
  }
}
```

## 4. 鉴权约定

- 使用 `Authorization: Bearer <token>` 传递 JWT
- JWT 载荷至少包含：`sub`、`username`、`roles`、`exp`
- 接口权限优先通过依赖注入方式控制，便于后续按模块组合

## 5. 后续补充

- 已补充数据库首版表结构，字段设计见 `docs/database-design.md`
- 分页、筛选、排序统一规范
- 错误码表与审计日志字段
- WebSocket/轮询通知协议
