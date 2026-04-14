<script lang="ts" setup>
import { Card, Col, Row, Space, Tag } from 'ant-design-vue';

defineOptions({ name: 'AdminContents' });

const rows = [
  {
    channel: '全平台',
    id: 'CNT-1',
    status: '已发布',
    title: '防骗文案：医保异常短信识别提醒',
    type: '防骗内容',
  },
  {
    channel: '子女端',
    id: 'CNT-2',
    status: '待审核',
    title: '提醒模板：先挂电话再核实',
    type: '提示模板',
  },
  {
    channel: '社区端',
    id: 'CNT-3',
    status: '已发布',
    title: '宣教案例：退款验证码骗局',
    type: '宣教内容',
  },
];
</script>

<template>
  <div class="admin-contents-page">
    <section class="hero-panel">
      <div>
        <p class="eyebrow">管理后台 / 内容资产</p>
        <h1>内容管理</h1>
        <p class="description">
          当前先完成防骗内容和模板列表展示，便于统一查看哪些素材已经可供多端复用。
        </p>
      </div>
    </section>

    <Row :gutter="[16, 16]" class="list-row">
      <Col v-for="item in rows" :key="item.id" :lg="8" :span="24">
        <Card class="content-card" :bordered="false">
          <Space wrap>
            <Tag color="blue">{{ item.type }}</Tag>
            <Tag>{{ item.channel }}</Tag>
            <Tag :color="item.status === '已发布' ? 'success' : 'warning'">{{ item.status }}</Tag>
          </Space>
          <h3>{{ item.title }}</h3>
          <p>{{ item.id }}</p>
        </Card>
      </Col>
    </Row>
  </div>
</template>

<style scoped>
.admin-contents-page {
  min-height: 100%;
  padding: 24px;
  background:
    radial-gradient(circle at top right, rgba(14, 165, 233, 0.12), transparent 28%),
    linear-gradient(180deg, #f7fcff 0%, #eef8ff 100%);
}

.hero-panel,
.content-card {
  border: 1px solid rgba(14, 165, 233, 0.14);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 16px 36px rgba(14, 116, 144, 0.08);
}

.hero-panel {
  padding: 28px 30px;
}

.eyebrow {
  margin: 0 0 12px;
  color: #0284c7;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.08em;
}

h1,
.content-card h3 {
  margin: 0;
  color: #0c4a6e;
}

h1 {
  font-size: 34px;
}

.description,
.content-card p {
  margin: 16px 0 0;
  color: #475569;
  line-height: 1.8;
}

.list-row {
  margin-top: 18px;
}

@media (max-width: 768px) {
  .admin-contents-page {
    padding: 16px;
  }

  h1 {
    font-size: 28px;
  }
}
</style>
