<script lang="ts" setup>
import PortalPage from '../../shared/portal-page.vue';
</script>

<template>
  <PortalPage
    accent="#dc2626"
    description="一键求助页用于缩短老人遇到风险时的操作路径，后续会接入快捷拨号、站内通知和社区联动提醒。"
    role="老年端"
    title="一键求助"
    :hero-stats="[
      { title: '第一联系人', description: '默认通知子女联系人并同步风险时间。' },
      { title: '社区支持', description: '高风险场景支持同步社区工作人员。' },
      { title: '操作要求', description: '页面保持大按钮、少步骤、强反馈。' },
    ]"
    :sections="[
      { title: '快捷拨号', description: '预留电话能力接入位置。' },
      { title: '紧急提醒', description: '预留向家属和社区发送高优先级消息。' },
      { title: '求助记录', description: '预留后续处置留痕和回访记录。' },
    ]"
  />
</template>
