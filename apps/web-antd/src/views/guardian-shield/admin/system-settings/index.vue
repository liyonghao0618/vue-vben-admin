<script lang="ts" setup>
import { Card, Col, Row, Space, Tag } from 'ant-design-vue';

defineOptions({ name: 'AdminSystemSettings' });

const rows = [
  {
    desc: '控制高风险时是否同步通知子女与社区。',
    group: '通知策略',
    key: 'risk_notice_strategy',
    status: '可编辑',
    value: '高风险同时通知家属和社区',
  },
  {
    desc: '控制风险列表默认每页展示数量。',
    group: '列表参数',
    key: 'default_page_size',
    status: '可编辑',
    value: '5',
  },
  {
    desc: '决定老年端是否默认启用大字号样式。',
    group: '适老设置',
    key: 'elder_large_font_default',
    status: '可编辑',
    value: '开启',
  },
];
</script>

<template>
  <div class="admin-system-settings-page">
    <section class="hero-panel">
      <div>
        <p class="eyebrow">管理后台 / 参数管理</p>
        <h1>系统配置</h1>
        <p class="description">
          当前页面已补齐基础参数展示和编辑入口说明，为后续真实配置表接入预留稳定结构。
        </p>
      </div>
    </section>

    <Row :gutter="[16, 16]" class="list-row">
      <Col v-for="item in rows" :key="item.key" :lg="8" :span="24">
        <Card class="setting-card" :bordered="false">
          <Space wrap>
            <Tag color="blue">{{ item.group }}</Tag>
            <Tag color="success">{{ item.status }}</Tag>
          </Space>
          <h3>{{ item.value }}</h3>
          <p class="key">{{ item.key }}</p>
          <p class="desc">{{ item.desc }}</p>
        </Card>
      </Col>
    </Row>
  </div>
</template>

<style scoped>
.admin-system-settings-page {
  min-height: 100%;
  padding: 24px;
  background:
    radial-gradient(circle at top right, rgba(99, 102, 241, 0.12), transparent 28%),
    linear-gradient(180deg, #f8f9ff 0%, #eef0ff 100%);
}

.hero-panel,
.setting-card {
  border: 1px solid rgba(99, 102, 241, 0.14);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 16px 36px rgba(67, 56, 202, 0.08);
}

.hero-panel {
  padding: 28px 30px;
}

.eyebrow {
  margin: 0 0 12px;
  color: #4f46e5;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.08em;
}

h1,
.setting-card h3 {
  margin: 0;
  color: #312e81;
}

h1 {
  font-size: 34px;
}

.description,
.key,
.desc {
  margin: 16px 0 0;
  color: #475569;
  line-height: 1.8;
}

.list-row {
  margin-top: 18px;
}

@media (max-width: 768px) {
  .admin-system-settings-page {
    padding: 16px;
  }

  h1 {
    font-size: 28px;
  }
}
</style>
