<script lang="ts" setup>
import { computed } from 'vue';

import { Card, Col, Row, Space, Switch, Tag } from 'ant-design-vue';

defineOptions({ name: 'AdminRules' });

const rows = computed(() => [
  {
    action: '提醒不要点击链接，建议联系家属核实。',
    enabled: true,
    id: 'RULE-1',
    level: '高风险',
    scene: '短信',
    title: '医保异常链接诱导',
  },
  {
    action: '提醒挂断电话，不透露身份信息和验证码。',
    enabled: true,
    id: 'RULE-2',
    level: '高风险',
    scene: '通话',
    title: '公检法安全账户话术',
  },
  {
    action: '提示用户通过官方平台处理退款。',
    enabled: false,
    id: 'RULE-3',
    level: '中风险',
    scene: '短信',
    title: '退款验证码套取',
  },
]);
</script>

<template>
  <div class="admin-rules-page">
    <section class="hero-panel">
      <div>
        <p class="eyebrow">管理后台 / 规则管理</p>
        <h1>风险规则</h1>
        <p class="description">
          当前先完成规则列表和启停状态展示，便于后续继续接入新增、编辑和版本控制。
        </p>
      </div>
    </section>

    <Row :gutter="[16, 16]" class="list-row">
      <Col v-for="item in rows" :key="item.id" :lg="8" :span="24">
        <Card class="rule-card" :bordered="false">
          <div class="card-head">
            <div>
              <h3>{{ item.title }}</h3>
              <p>{{ item.id }} · {{ item.scene }}</p>
            </div>
            <Switch :checked="item.enabled" />
          </div>
          <Space wrap>
            <Tag color="red">{{ item.level }}</Tag>
            <Tag color="blue">{{ item.scene }}</Tag>
            <Tag :color="item.enabled ? 'success' : 'default'">
              {{ item.enabled ? '启用中' : '已停用' }}
            </Tag>
          </Space>
          <div class="block">
            <p class="label">建议动作</p>
            <p class="value">{{ item.action }}</p>
          </div>
        </Card>
      </Col>
    </Row>
  </div>
</template>

<style scoped>
.admin-rules-page {
  min-height: 100%;
  padding: 24px;
  background:
    radial-gradient(circle at top right, rgba(245, 158, 11, 0.12), transparent 28%),
    linear-gradient(180deg, #fffdf7 0%, #fff7e8 100%);
}

.hero-panel,
.rule-card {
  border: 1px solid rgba(245, 158, 11, 0.16);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 16px 36px rgba(146, 64, 14, 0.08);
}

.hero-panel {
  padding: 28px 30px;
}

.eyebrow {
  margin: 0 0 12px;
  color: #d97706;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.08em;
}

h1 {
  margin: 0;
  color: #92400e;
  font-size: 34px;
}

.description {
  margin: 16px 0 0;
  color: #78350f;
  line-height: 1.8;
}

.list-row {
  margin-top: 18px;
}

.card-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 14px;
}

.card-head h3 {
  margin: 0;
  color: #92400e;
}

.card-head p,
.value {
  margin: 8px 0 0;
  color: #78350f;
  line-height: 1.8;
}

.block {
  margin-top: 16px;
}

.label {
  margin: 0;
  color: #b45309;
  font-weight: 700;
}

@media (max-width: 768px) {
  .admin-rules-page {
    padding: 16px;
  }

  .card-head {
    flex-direction: column;
  }

  h1 {
    font-size: 28px;
  }
}
</style>
