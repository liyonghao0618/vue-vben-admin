<script lang="ts" setup>
import PortalPage from '../../shared/portal-page.vue';
</script>

<template>
  <PortalPage
    accent="#1d4ed8"
    description="统计报表页用于沉淀辖区风险趋势、工单处置效率和宣教覆盖情况，为后续汇报和复盘提供依据。"
    role="社区端"
    title="统计报表"
    :hero-stats="[
      { title: '风险趋势', description: '按日、周、月展示告警数量变化。' },
      { title: '处置效率', description: '统计从告警到完结的平均时长。' },
      { title: '宣传覆盖', description: '跟踪重点宣教内容的覆盖人数。' },
    ]"
    :sections="[
      { title: '图表区域', description: '后续接入趋势图、分布图和排行图。' },
      { title: '导出能力', description: '预留导出周报、月报和专项统计。' },
      { title: '复盘分析', description: '帮助社区优化重点人群与处置策略。' },
    ]"
  />
</template>
