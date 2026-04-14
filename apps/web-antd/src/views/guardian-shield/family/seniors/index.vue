<script lang="ts" setup>
import PortalPage from '../../shared/portal-page.vue';
</script>

<template>
  <PortalPage
    accent="#0f766e"
    description="老人列表页用于查看监护对象的绑定关系、风险状态和最近一次告警时间。"
    role="子女端"
    title="老人列表"
    :hero-stats="[
      { title: '绑定关系', description: '支持展示父母、祖辈等监护关系。' },
      { title: '风险状态', description: '保留正常、关注、高风险标签。' },
      { title: '最近联系', description: '后续关联远程提醒和回访记录。' },
    ]"
    :sections="[
      { title: '基础信息', description: '展示姓名、年龄、联系方式和社区信息。' },
      { title: '风险摘要', description: '展示近期高频诈骗类型和告警次数。' },
      { title: '进入详情', description: '跳转查看个人风险详情与通知历史。' },
    ]"
  />
</template>
