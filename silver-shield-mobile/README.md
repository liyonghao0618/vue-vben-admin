# Silver Shield Mobile Apps

# 先用 H5 开发和调试，最终进度达到 95% 的时候移动到微信小程序进行测试

`silver-shield-mobile-apps` 是“守护桑榆 / Silver Shield AI”体系下的移动端项目，用于承载老年用户端与子女 / 守护人端的双角色通信与反诈守护能力。

当前仓库已经完成 P0 工程初始化，并采用 `uni-app + Vue3 + Vite + TypeScript` 作为基础技术栈，优先以 H5 方式开发和联调，后续再迁移到微信小程序进行专项测试。

## 当前结论

- 产品形态：一个应用双角色
- 开发策略：H5 优先，后期迁移到微信小程序验证
- 状态管理：`Pinia`
- 导航方案：`uni-app` 原生页面导航
- UI 方案：原生基础组件 + 项目自定义基础组件
- AI 接口：对接 `ai-api-service`
- 主业务接口：登录、绑定关系、风险通知、求助、聊天由主业务系统承载

## 目录结构

```text
silver-shield-mobile/
├── README.md
├── TODO.md
├── 需求分析文档.md
├── .env.example
├── docs/
│   ├── h5-debug.md
│   └── p0-architecture.md
├── src/
│   ├── api/
│   ├── components/
│   ├── pages/
│   ├── static/
│   ├── store/
│   ├── types/
│   ├── utils/
│   ├── App.vue
│   ├── main.ts
│   ├── manifest.json
│   ├── pages.json
│   └── uni.scss
└── uni_modules/
```

## 启动开发

```bash
npm install
npm run dev:h5
```

演示模式：

```bash
npm run dev:h5:demo
```

## 当前能力

- 登录与角色分流
- 老年端：首页、联系人、会话列表、聊天、风险提醒、求助、适老化设置、通话页、通话记录
- 守护人端：总览、老人列表、风险通知、风险详情、聊天、求助详情、通话页、通话记录
- AI 风险识别：文本、聊天记录、链接、图片 OCR 预留、通话后复盘提醒
- 主业务系统联调骨架：登录、用户信息、绑定关系、风险通知、求助
- 守护增强：风险趋势统计、重点联系人、黑名单标记、社区协同入口
- 环境模式：`development` / `demo` / `production`

## 下一阶段

P1 将继续推进：

1. 增补更多自动化测试与联调验收记录
2. 补齐图片消息识别、OCR 和通话摘要分析
3. 推进埋点、日志和崩溃监控接入
4. 完成微信小程序专项验证

## 相关文档

- [需求分析文档](/workspaces/silver-shield-mobile/需求分析文档.md)
- [项目 TODO](/workspaces/silver-shield-mobile/TODO.md)
- [P0 架构结论](/workspaces/silver-shield-mobile/docs/p0-architecture.md)
- [H5 调试说明](/workspaces/silver-shield-mobile/docs/h5-debug.md)
- [服务联调说明](/workspaces/silver-shield-mobile/docs/service-integration.md)
- [工程完善方案](/workspaces/silver-shield-mobile/docs/engineering-plan.md)
- [合规与安全说明](/workspaces/silver-shield-mobile/docs/compliance-security.md)
- [手工测试清单](/workspaces/silver-shield-mobile/docs/manual-test-checklist.md)
- [测试计划](/workspaces/silver-shield-mobile/docs/test-plan.md)
