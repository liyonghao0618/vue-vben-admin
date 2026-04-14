<script lang="ts" setup>
import PortalPage from '../../shared/portal-page.vue';
</script>

<template>
  <PortalPage
    accent="#65a30d"
    description="防骗知识页承接图文案例、语音播报和常见骗局说明，当前阶段先完成信息结构和页面入口。"
    role="老年端"
    title="防骗知识"
    :hero-stats="[
      { title: '常见骗局', description: '冒充公检法、中奖返利、熟人借钱等。' },
      { title: '适老阅读', description: '后续支持大字模式和朗读播放。' },
      { title: '重点提示', description: '突出“不轻信、不转账、不点链接”。' },
    ]"
    :sections="[
      { title: '案例库', description: '预留诈骗案例和社区宣教内容入口。' },
      { title: '提示模板', description: '接入后台可配置的防骗提示文案。' },
      { title: '操作指引', description: '帮助老人快速核实、求助和反馈。' },
    ]"
  />
</template>
