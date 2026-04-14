<script lang="ts" setup>
import PortalPage from '../../shared/portal-page.vue';
</script>

<template>
  <PortalPage
    accent="#2563eb"
    description="子女端首页用于总览老人近期风险、通知状态和重点关注对象，当前已接通角色首页跳转。"
    role="子女端首页"
    title="监护总览"
    :hero-stats="[
      { title: '监护老人', description: '当前管理 2 位老人，1 位处于重点关注。' },
      { title: '近 7 日告警', description: '共 5 条，其中 2 条为高风险。' },
      { title: '待处理通知', description: '1 条告警尚未确认处置。' },
    ]"
    :sections="[
      { title: '趋势总览', description: '预留近 7 日和近 30 日风险趋势图。' },
      { title: '重点提醒', description: '突出高风险事件和系统建议动作。' },
      { title: '处置反馈', description: '接入已读状态与远程提醒反馈。' },
    ]"
  />
</template>
