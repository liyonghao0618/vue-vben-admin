<script lang="ts" setup>
import PortalPage from '../../shared/portal-page.vue';
</script>

<template>
  <PortalPage
    accent="#0284c7"
    description="亲属绑定页用于管理 1 至 3 名监护人，并为后续高风险通知和远程提醒能力打通基础数据关系。"
    role="老年端"
    title="亲属绑定"
    :hero-stats="[
      { title: '绑定上限', description: '支持最多绑定 3 名亲属。' },
      { title: '授权状态', description: '后续展示绑定码、邀请码和授权有效期。' },
      { title: '通知优先级', description: '高风险事件优先推送主联系人。' },
    ]"
    :sections="[
      { title: '新增亲属', description: '预留录入手机号、关系和备注信息。' },
      { title: '解绑管理', description: '支持修改、解绑和重新授权。' },
      { title: '安全确认', description: '保留关键操作二次确认与留痕。' },
    ]"
  />
</template>
