<script lang="ts" setup>
import PortalPage from '../../shared/portal-page.vue';
</script>

<template>
  <PortalPage
    accent="#059669"
    description="内容管理页用于统一维护诈骗案例、防骗文案和社区宣教素材，为多端复用提供统一来源。"
    role="管理后台"
    title="内容管理"
    :hero-stats="[
      { title: '内容类型', description: '案例库、提示模板、宣教素材统一管理。' },
      { title: '发布对象', description: '支持老年端、子女端、社区端多端分发。' },
      { title: '复用能力', description: '作为后续知识库和宣教页的数据来源。' },
    ]"
    :sections="[
      { title: '案例维护', description: '沉淀真实诈骗案例和防骗解读。' },
      { title: '模板维护', description: '统一管理风险提示与远程提醒模板。' },
      { title: '素材管理', description: '管理社区宣教图文和海报资源。' },
    ]"
  />
</template>
