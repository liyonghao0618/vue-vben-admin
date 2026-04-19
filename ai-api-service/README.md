# AI API Service

## 模块定位

`ai-api-service` 是一个放置在仓库根目录的独立后端模块，专门用于提供“诈骗内容识别”相关的 AI API 服务。

这个模块的核心目标是：

- 完全独立于当前 `vue-vben-admin` 主项目
- 可以单独开发、单独部署、单独运维
- 未来部署在另一台服务器上
- 当前阶段先在 Codespaces 环境中运行和验证
- 不依赖当前仓库内的 `apps`、`packages`、`internal` 等任何现有模块

换句话说，它虽然和前端项目放在同一个仓库根目录下，但工程上应视为一个外部服务。

## 主要用途

这个模块专门面向诈骗识别场景，后续主要提供以下能力：

- 输入一段文本，判断是否存在诈骗风险
- 对风险类型进行分类，例如冒充客服、刷单返利、虚假投资、中奖诈骗、钓鱼链接等
- 返回风险等级、命中原因、关键可疑片段和简短建议
- 为前端提供统一、稳定、可扩展的 HTTP API

当前阶段优先支持文本识别，后续再考虑扩展到截图 OCR 后识别、聊天记录批量分析、链接辅助判定等能力。

## 模型方案

当前模型展示与默认方案使用 `Qwen` 系列，并优先选择尽量小的模型，以适配 Codespaces 的有限资源。

推荐原则如下：

- 默认优先考虑小模型，先保证“能跑起来”
- 初期应优先使用 `Qwen2.5-1.5B-Instruct` 或同等级别的小模型
- 如果 Codespaces 资源依然吃紧，可以继续降级到更轻量的推理方案，或通过远程模型服务调用
- 在服务结构上保留模型切换能力，后续再升级到更强模型

之所以优先小模型，是因为当前运行环境不是正式推理服务器，而是开发期的 Codespaces。此时资源占用、启动速度和调试体验比极限效果更重要。

## 设计原则

- 独立仓库思维：虽然目录位于当前仓库根目录，但按“外部诈骗识别服务”来设计
- 零耦合：不要直接引用主项目中的组件、工具函数、类型、配置或构建体系
- 资源克制：优先选择轻量实现，减少对 CPU、内存和磁盘的消耗
- 可替换：模型层应支持未来从本地小模型切换到远程推理服务
- 可部署：默认考虑 Linux 服务器、Docker 容器、反向代理、环境变量配置
- 可扩展：后续可逐步加入鉴权、限流、日志、审计、提示词版本管理与规则增强

## 与主项目的边界

这个模块和前端主项目之间建议通过 HTTP/HTTPS API 通信，不共享运行时、不共享构建产物、不共享内部代码。

建议边界如下：

- 前端项目只负责调用该服务暴露出的接口
- 诈骗识别服务只负责风险分析、模型调用、规则补充、结果封装与安全控制
- 双方通过明确的接口协议协作，例如 REST
- 当前阶段优先做同步 JSON API，流式输出不是首要目标

## 计划中的接口方向

后续首批接口建议聚焦在最小可用能力：

- `GET /health`
  用于健康检查，确认服务可用
- `POST /api/fraud-detect`
  输入待识别文本，返回诈骗风险分析结果
- `POST /api/fraud-detect/batch`
  输入多条文本，返回批量识别结果
- `POST /api/fraud-detect/chat-log`
  输入聊天记录数组，返回整体风险和逐条分析
- `POST /api/fraud-detect/link`
  输入单个链接，返回链接辅助风险判断
- `POST /api/review`
  提交人工复核结果并记录审计日志

建议返回字段包括：

- `isFraud`: 是否疑似诈骗
- `riskLevel`: 风险等级，例如 `low`、`medium`、`high`
- `category`: 风险类别
- `reason`: 简要判定原因
- `evidence`: 命中的可疑内容片段
- `suggestion`: 给用户的处理建议
- `model`: 当前使用的模型名称
- `traceId`: 当前分析请求的唯一标识
- `promptVersion`: 当前提示词版本

## 目录约定

当前目录结构：

```text
ai-api-service/
├── README.md
└── TODO.md
```

建议后续演进为：

```text
ai-api-service/
├── README.md
├── TODO.md
├── package.json
├── .gitignore
├── .env.example
├── .dockerignore
├── src/
│   ├── app/
│   ├── config/
│   ├── modules/
│   ├── prompts/
│   ├── routes/
│   ├── services/
│   └── utils/
├── test/
├── scripts/
├── Dockerfile
└── docker-compose.yml
```

## 推荐实现思路

为了先在 Codespaces 跑通，建议实现顺序尽量简单：

1. 先做一个轻量 Node.js API 服务，例如 `Node.js + Fastify`
2. 先只支持文本输入，不做文件上传和多模态
3. 先做单接口诈骗识别，再逐步补充批量识别
4. 先用固定提示词 + 小模型输出结构化 JSON
5. 必要时增加少量规则兜底，例如关键词、链接、转账、验证码、下载诱导等高风险信号

这样能尽快拿到一个可测、可调用、可演示的最小版本。

## 暂不纳入主工程

为了保证它的隔离性，当前建议保持以下约束：

- 不加入根目录 `pnpm-workspace.yaml`
- 不复用主项目的 ESLint、TSConfig、构建脚本和发布流程
- 不直接引用主项目中的代码
- 不让主项目构建流程默认扫描或打包这个模块

这样做可以确保它未来拆分到独立仓库或迁移到其他服务器时成本最低。

## 运行环境约束

当前阶段需要显式考虑 Codespaces 的开发资源限制：

- 内存和 CPU 资源有限，不适合直接跑过大的本地模型
- 首次拉取模型可能较慢，应避免过大的模型体积
- 应优先保证本地开发、接口联调和功能验证，而不是追求最终效果上限

因此，当前文档默认采用“小模型优先、结构预留升级”的策略。

## 当前状态

当前目录已经完成 `P0` 最小版本，可作为独立诈骗识别 API 服务启动运行，现阶段仍不参与现有项目构建与运行。详细开发拆解见 [TODO.md](/workspaces/vue-vben-admin/ai-api-service/TODO.md)。

目前还已经完成远程 Qwen 兼容接口接入验证：

- `.env.local` 可直接填写远程兼容地址与 API Key
- 服务启动时会自动读取 `.env.local`
- 已验证远程模型可实际返回结构化识别结果
- 正常返回时会看到 `provider: "qwen"` 与 `fallbackUsed: false`
- 当远程模型不可用或输出不合规时，仍会自动退回本地规则识别

## 当前已实现内容

当前版本已经具备以下能力：

- 独立 `Node.js + Fastify` 服务骨架
- `GET /health` 健康检查接口
- `POST /api/fraud-detect` 单条文本诈骗识别接口
- `POST /api/fraud-detect/batch` 批量识别接口
- `POST /api/fraud-detect/chat-log` 聊天记录批量分析接口
- `POST /api/fraud-detect/link` 链接风险辅助分析接口
- `POST /api/review` 人工复核接口
- `Qwen` 优先的小模型配置入口，默认模型为 `Qwen2.5-1.5B-Instruct`
- 支持远程 Qwen 兼容接口接入，并已验证可用
- 未配置远程 Qwen 接口或远程输出异常时的本地规则兜底
- 统一的 JSON 响应结构和基础参数校验
- 基于内存的轻量限流能力
- 可选的 Bearer Token 鉴权预留
- 提示词版本标识与联合判定模式字段
- 审计日志写入能力
- 基于 `node:test` 的接口测试

## 快速启动

在 `ai-api-service` 目录内运行：

```bash
npm install
npm start
```

默认监听：

```text
http://127.0.0.1:3001
```

开发模式：

```bash
npm run dev
```

构建命令：

```bash
npm run build
```

运行测试：

```bash
npm test
```

环境变量可以参考：

```bash
cp .env.example .env
```

当前仓库里也已经为你预留了本地填写位置：

```bash
ai-api-service/.env.local
```

你主要只需要填写这两个字段：

```bash
QWEN_BASE_URL=https://your-qwen-endpoint.example.com/v1
QWEN_API_KEY=your_api_key_here
```

服务启动时会自动读取 `.env.local`，你填完后直接运行：

```bash
npm start
```

如果远程 Qwen 配置正确且模型返回了结构化 JSON，主接口返回里会包含类似字段：

```json
{
  "provider": "qwen",
  "fallbackUsed": false,
  "decisionMode": "model+rules"
}
```

## 接口示例

请求：

```bash
curl -X POST http://127.0.0.1:3001/api/fraud-detect \
  -H 'Content-Type: application/json' \
  -d '{
    "text": "您好，我是平台客服，您的账户异常需要立即点击链接验证并提供短信验证码完成解冻。",
    "scene": "chat",
    "source": "demo"
  }'
```

示例响应：

```json
{
  "data": {
    "category": "impersonation-support",
    "categoryLabel": "冒充客服或官方",
    "evidence": ["客服", "账户异常", "点击链接", "验证码"],
    "isFraud": true,
    "reason": "文本出现冒充客服或平台官方处理问题的话术。",
    "riskLevel": "high",
    "score": 9,
    "suggestion": "请勿转账、勿点击陌生链接、勿透露验证码，必要时联系官方渠道核实。",
    "fallbackUsed": true,
    "model": "Qwen2.5-1.5B-Instruct",
    "promptVersion": "fraud-detect/v1",
    "provider": "rules-fallback",
    "providerReason": "Remote Qwen endpoint is not configured.",
    "traceId": "generated-uuid"
  }
}
```

远程 Qwen 生效时，响应会更接近下面这种形式：

```json
{
  "data": {
    "traceId": "generated-uuid",
    "category": "impersonation-support",
    "categoryLabel": "冒充客服或官方",
    "evidence": ["我是平台客服", "立即点击链接", "提供短信验证码"],
    "isFraud": true,
    "reason": "冒充客服以账户解冻为由诱导点击链接并索要短信验证码。",
    "riskLevel": "high",
    "suggestion": "切勿点击陌生链接或提供验证码，请通过官方渠道核实身份并立即举报。",
    "decisionMode": "model+rules",
    "fallbackUsed": false,
    "model": "your-qwen-model",
    "promptVersion": "fraud-detect/v1",
    "provider": "qwen"
  }
}
```

聊天记录分析请求：

```bash
curl -X POST http://127.0.0.1:3001/api/fraud-detect/chat-log \
  -H 'Content-Type: application/json' \
  -d '{
    "messages": [
      { "role": "user", "text": "你好" },
      { "role": "agent", "text": "我是平台客服，请点击链接并提供验证码完成解冻。" }
    ]
  }'
```

链接分析请求：

```bash
curl -X POST http://127.0.0.1:3001/api/fraud-detect/link \
  -H 'Content-Type: application/json' \
  -d '{ "link": "http://198.51.100.12/login?redirect=bank" }'
```

## 当前模型策略

当前默认策略如下：

- 展示模型固定为 `Qwen`
- 默认模型名为 `Qwen2.5-1.5B-Instruct`
- 如果配置了兼容 OpenAI 风格的远程 Qwen 接口，则优先调用模型
- 如果没有配置远程接口，或远程模型未返回可解析的结构化 JSON，则自动退回本地规则识别

这套策略适合当前 Codespaces 阶段的轻量开发与联调。

## 访问控制

当前版本提供两种轻量保护手段：

- `API_TOKEN`
  设置后，除 `/health` 之外的接口都需要携带 `Authorization: Bearer <token>`
- `RATE_LIMIT_WINDOW_MS` 与 `RATE_LIMIT_MAX_REQUESTS`
  用于启用基于内存的基础限流，适合当前 Codespaces 开发环境

示例：

```bash
API_TOKEN=demo-token RATE_LIMIT_MAX_REQUESTS=10 npm start
```

## 环境变量说明

当前支持的主要环境变量如下：

- `PORT`
  服务监听端口，默认 `3001`
- `HOST`
  服务监听地址，默认 `0.0.0.0`
- `LOG_LEVEL`
  日志级别，默认 `info`
- `QWEN_MODEL`
  展示与默认使用的模型名，默认 `Qwen2.5-1.5B-Instruct`
- `QWEN_BASE_URL`
  远程 Qwen 兼容接口的基础地址
- `QWEN_API_KEY`
  远程 Qwen 接口的访问密钥
- `QWEN_CHAT_PATH`
  聊天补全接口路径，默认 `/chat/completions`
- `API_TOKEN`
  可选的 Bearer Token 鉴权密钥
- `RATE_LIMIT_WINDOW_MS`
  限流时间窗口，默认 `60000`
- `RATE_LIMIT_MAX_REQUESTS`
  时间窗口内允许的最大请求数，默认 `30`

## Docker 部署

构建镜像：

```bash
docker build -t ai-api-service .
```

也可以直接使用：

```bash
docker compose up --build
```

运行容器：

```bash
docker run --rm -p 3001:3001 \
  -e API_TOKEN=demo-token \
  -e RATE_LIMIT_MAX_REQUESTS=30 \
  ai-api-service
```

如果需要接入远程 Qwen 兼容接口，可以继续传入：

```bash
-e QWEN_BASE_URL=https://your-qwen-endpoint.example.com \
-e QWEN_API_KEY=your-api-key \
-e QWEN_MODEL=Qwen2.5-1.5B-Instruct
```

## 部署建议

当前部署建议如下：

- 在 Codespaces 阶段继续使用“远程 Qwen + 本地规则兜底”的模式
- 不建议在 Codespaces 内直接拉取过大的本地模型文件
- 如果后续迁移到独立服务器，再评估是否改成本地模型推理
- 上线时建议在反向代理层补充 HTTPS、来源限制和更稳定的限流策略

## 模型下载与缓存评估

当前实现默认不在本地下载模型文件，而是优先通过远程 Qwen 兼容接口调用模型；未配置时退回本地规则识别。

这样做的原因是：

- Codespaces 磁盘和内存资源有限
- 大模型下载和冷启动时间不稳定
- 当前阶段目标是优先完成接口联调和业务验证

如果后续要切换为本地模型部署，再单独评估：

- 模型文件体积
- 首次下载耗时
- 容器镜像大小
- 推理启动时间
- CPU 与内存占用

基于当前 Codespaces 环境的结论：

- 当前阶段不建议在本地容器内预置 Qwen 模型文件
- 模型下载、缓存和启动时间的主评估结论是“优先远程调用，避免本地冷启动成本”
- 只有在迁移到独立服务器并确认磁盘、内存和启动预算后，才适合继续评估本地模型部署
