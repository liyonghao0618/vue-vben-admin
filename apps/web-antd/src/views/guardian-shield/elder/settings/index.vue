<script lang="ts" setup>
import PortalPage from '../../shared/portal-page.vue';
</script>

<template>
  <PortalPage
    accent="#7c3aed"
    description="适老设置页聚焦字号、对比度、提醒方式和语音辅助，是后续提升可用性的关键页面。"
    role="老年端"
    title="适老设置"
    :hero-stats="[
      { title: '大字号', description: '默认采用更高可读性的文本尺寸。' },
      { title: '高对比度', description: '保留浅底深字与重点风险色强调。' },
      { title: '语音辅助', description: '后续接入读屏与语音播报。' },
    ]"
    :sections="[
      { title: '显示设置', description: '控制字号、间距和按钮尺寸。' },
      { title: '提醒设置', description: '管理风险提示和求助反馈方式。' },
      { title: '隐私授权', description: '承接数据采集范围与授权说明。' },
    ]"
  />
</template>
