<script lang="ts" setup>
import PortalPage from '../../shared/portal-page.vue';
</script>

<template>
  <PortalPage
    accent="#65a30d"
    description="宣教管理页负责安排社区防骗内容投放，后续可按社区、人群和时间维度进行发布与查看。"
    role="社区端"
    title="宣教管理"
    :hero-stats="[
      { title: '内容类型', description: '图文、海报、案例解读、音频播报。' },
      { title: '投放范围', description: '支持按社区和目标人群定向推送。' },
      { title: '宣传计划', description: '可承接月度和专项反诈活动。' },
    ]"
    :sections="[
      { title: '内容库', description: '关联后台统一维护的宣教素材。' },
      { title: '发布记录', description: '追踪内容发布时间和覆盖对象。' },
      { title: '效果反馈', description: '后续统计阅读、回访和参与情况。' },
    ]"
  />
</template>
