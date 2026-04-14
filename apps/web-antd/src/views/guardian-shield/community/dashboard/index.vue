<script lang="ts" setup>
import PortalPage from '../../shared/portal-page.vue';
</script>

<template>
  <PortalPage
    accent="#0f766e"
    description="社区端总览承接辖区老年用户、重点对象与高风险事件统计，用于社区人员快速判断当天工作重点。"
    role="社区端首页"
    title="辖区总览"
    :hero-stats="[
      { title: '辖区老人', description: '当前接入 128 位老人基础档案。' },
      { title: '高风险事件', description: '今日新增 3 条，需尽快回访。' },
      { title: '待办工单', description: '2 条工单待转派或归档。' },
    ]"
    :sections="[
      { title: '风险分布', description: '展示辖区风险级别和诈骗类型分布。' },
      { title: '重点对象', description: '聚焦近期连续告警或独居老人。' },
      { title: '处置效率', description: '后续统计回访、宣教和完结时效。' },
    ]"
  />
</template>
