<script lang="ts" setup>
import PortalPage from '../../shared/portal-page.vue';
</script>

<template>
  <PortalPage
    accent="#dc2626"
    description="风险规则页承接短信和通话文本的规则配置，当前页面骨架已预留词库、规则和建议动作配置区。"
    role="管理后台"
    title="风险规则"
    :hero-stats="[
      { title: '规则类型', description: '关键词、模式匹配、黑白名单。' },
      { title: '风险分级', description: '低、中、高三级输出与原因说明。' },
      { title: '版本迭代', description: '预留规则版本和生效时间管理。' },
    ]"
    :sections="[
      { title: '规则列表', description: '管理诈骗话术和命中策略。' },
      { title: '风险词库', description: '维护高频诈骗关键词和场景标签。' },
      { title: '建议动作', description: '配置不同风险级别的提醒模板。' },
    ]"
  />
</template>
