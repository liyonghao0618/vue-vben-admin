<script lang="ts" setup>
import PortalPage from '../../shared/portal-page.vue';
</script>

<template>
  <PortalPage
    accent="#0891b2"
    description="重点老人页用于查看辖区内需要重点跟进的对象，并记录风险标签、走访状态和社区联系人。"
    role="社区端"
    title="重点老人"
    :hero-stats="[
      { title: '关注标签', description: '支持独居、频繁告警、需回访等标签。' },
      { title: '联系状态', description: '显示最近一次电话或入户时间。' },
      { title: '协同信息', description: '关联子女联系人和处置工单。' },
    ]"
    :sections="[
      { title: '档案信息', description: '后续展示家庭关系、所属网格和备注。' },
      { title: '回访动作', description: '记录电话回访、走访、宣教等动作。' },
      { title: '风险追踪', description: '汇总历史告警与处理结果。' },
    ]"
  />
</template>
