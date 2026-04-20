# 服务联调说明

## 当前状态

当前移动端已经接入两类后端：

- 主业务系统：登录、用户信息、绑定关系、风险通知、求助
- `ai-api-service`：文本识别、聊天记录识别、链接识别

所有接口均采用“真实接口优先，失败后自动回退演示数据”的方式，便于 H5 阶段持续开发。

## 已接入接口

### 主业务系统

- `POST /api/mobile/auth/login`
- `GET /api/mobile/users/me`
- `GET /api/mobile/relations`
- `GET /api/mobile/alerts`
- `POST /api/mobile/sos`

对应文件：

- [src/api/main.ts](/workspaces/silver-shield-mobile/src/api/main.ts)
- [src/api/sos.ts](/workspaces/silver-shield-mobile/src/api/sos.ts)
- [src/api/http.ts](/workspaces/silver-shield-mobile/src/api/http.ts)

### AI 服务

- `POST /api/fraud-detect`
- `POST /api/fraud-detect/chat-log`
- `POST /api/fraud-detect/link`

对应文件：

- [src/api/fraud.ts](/workspaces/silver-shield-mobile/src/api/fraud.ts)

## 环境变量

- `VITE_API_BASE_URL`：主业务系统地址
- `VITE_AI_API_BASE_URL`：AI 服务地址
- `VITE_APP_ENV`：`development` / `demo` / `production`
- `VITE_API_TIMEOUT`：请求超时时间，单位毫秒

已提供：

- [.env.example](/workspaces/silver-shield-mobile/.env.example)
- [.env.demo](/workspaces/silver-shield-mobile/.env.demo)
- [.env.production](/workspaces/silver-shield-mobile/.env.production)

## 联调策略

### H5 开发模式

- 使用 `npm run dev:h5`
- 默认读取本地环境变量
- 如果真实后端暂不可用，会自动回退到演示数据

### 演示模式

- 使用 `npm run dev:h5:demo`
- 强制使用本地 fallback 数据
- 适合路演、离线演示、UI 走查

## 鉴权说明

- 登录成功后，token 会写入本地存储 `silver-shield-mobile-auth-token`
- 后续请求会自动带上 `Authorization: Bearer <token>`
- 退出登录时会清除 token

## 建议后端返回结构

### 登录

```json
{
  "token": "jwt-or-session-token",
  "user": {
    "id": "guardian-001",
    "name": "李女士",
    "role": "guardian",
    "phone": "13900001111",
    "welcomeText": "今天有 1 条高风险提醒待查看。"
  }
}
```

### 绑定关系

```json
{
  "contacts": [],
  "elders": []
}
```

### 风险通知

```json
{
  "records": []
}
```
