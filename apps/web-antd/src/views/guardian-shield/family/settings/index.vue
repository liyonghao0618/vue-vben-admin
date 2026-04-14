<script lang="ts" setup>
import PortalPage from '../../shared/portal-page.vue';
</script>

<template>
  <PortalPage
    accent="#4f46e5"
    description="监护设置页用于配置提醒偏好、模板消息和家庭监护规则，是后续通知体验的配置入口。"
    role="子女端"
    title="监护设置"
    :hero-stats="[
      { title: '提醒模板', description: '预设“不要转账”“先挂电话再核实”等文案。' },
      { title: '通知偏好', description: '区分高风险必达与普通提醒。' },
      { title: '监护范围', description: '管理绑定对象和接收授权。' },
    ]"
    :sections="[
      { title: '消息模板', description: '承接后台可配置的提醒模板。' },
      { title: '提醒方式', description: '控制站内通知频率和优先级。' },
      { title: '授权管理', description: '预留解绑、续期和安全确认流程。' },
    ]"
  />
</template>
