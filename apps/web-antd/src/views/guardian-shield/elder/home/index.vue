<script lang="ts" setup>
import PortalPage from '../../shared/portal-page.vue';
</script>

<template>
  <PortalPage
    accent="#d97706"
    description="面向老年用户的首页先聚焦三件事：看懂风险、快速求助、及时联系家人。当前版本已经接通基础角色入口，后续会继续联动真实识别结果。"
    role="老年端首页"
    title="守护桑榆，让提醒更简单"
    :hero-stats="[
      { title: '今日风险提醒', description: '2 条待查看，包含 1 条高风险短信。' },
      { title: '紧急联系人', description: '已绑定 2 位家属与 1 位社区联系人。' },
      { title: '最近提示', description: '系统已提醒“陌生链接不要点开”。' },
    ]"
    :sections="[
      { title: '风险提醒', description: '用更大字号和更少信息密度展示结果，方便快速理解。' },
      { title: '一键求助', description: '后续可接入电话、站内通知和社区联动。' },
      { title: '亲属绑定', description: '当前阶段优先验证绑定入口和信息架构。' },
    ]"
  />
</template>
