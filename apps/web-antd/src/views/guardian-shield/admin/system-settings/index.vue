<script lang="ts" setup>
import PortalPage from '../../shared/portal-page.vue';
</script>

<template>
  <PortalPage
    accent="#475569"
    description="系统配置页承担运行参数、通知策略和基础字典的管理职责，当前先作为后台配置入口进行占位。"
    role="管理后台"
    title="系统配置"
    :hero-stats="[
      { title: '通知配置', description: '预留站内通知、短信等渠道参数。' },
      { title: '字典配置', description: '管理风险类型、工单状态等基础字典。' },
      { title: '运行参数', description: '预留轮询间隔、阈值和开关项。' },
    ]"
    :sections="[
      { title: '参数中心', description: '集中管理系统级配置。' },
      { title: '渠道管理', description: '后续接入消息推送与第三方通知配置。' },
      { title: '合规设置', description: '承接授权、隐私与审计相关参数。' },
    ]"
  />
</template>
