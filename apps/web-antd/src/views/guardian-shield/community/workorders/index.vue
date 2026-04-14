<script lang="ts" setup>
import PortalPage from '../../shared/portal-page.vue';
</script>

<template>
  <PortalPage
    accent="#c2410c"
    description="风险工单页负责承接需要社区介入的事件，后续将支持创建、转派、处理、归档和附件上传。"
    role="社区端"
    title="风险工单"
    :hero-stats="[
      { title: '工单状态', description: '待受理、处理中、已完成、已归档。' },
      { title: '转派协同', description: '支持网格员之间转派和备注交接。' },
      { title: '留痕要求', description: '关键处置动作保留审计记录。' },
    ]"
    :sections="[
      { title: '事件创建', description: '由高风险告警自动或人工生成工单。' },
      { title: '处置记录', description: '沉淀电话回访、上门处理和结果说明。' },
      { title: '附件上传', description: '预留回访截图和材料存档能力。' },
    ]"
  />
</template>
