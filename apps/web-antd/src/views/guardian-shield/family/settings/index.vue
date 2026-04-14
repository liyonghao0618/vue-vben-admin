<script lang="ts" setup>
import { ref } from 'vue';

import { Button, Card, Col, Input, Row, Space, Switch, Tag } from 'ant-design-vue';

defineOptions({ name: 'FamilySettings' });

const smsEnabled = ref(true);
const appEnabled = ref(true);
const voiceEnabled = ref(false);

const templates = ref([
  '先别转账，我马上给你回电话。',
  '验证码不要告诉别人，等我核实后再处理。',
  '先挂电话，确认是官方号码再联系。',
]);
</script>

<template>
  <div class="family-settings-page">
    <section class="hero-panel">
      <div>
        <p class="eyebrow">子女端 / 监护设置</p>
        <h1>监护设置</h1>
        <p class="description">
          配置您希望收到提醒的方式，并提前准备常用提醒文案。看到高风险事件时，可以更快做出干预。
        </p>
      </div>
      <div class="hero-note">
        <strong>建议</strong>
        <span>至少保留站内提醒和短信两种方式，避免单一渠道漏掉通知。</span>
      </div>
    </section>

    <Row :gutter="[16, 16]" class="content-row">
      <Col :lg="10" :span="24">
        <Card class="setting-card" :bordered="false" title="提醒方式">
          <div class="setting-item">
            <div>
              <h3>站内提醒</h3>
              <p>适合第一时间查看完整事件详情。</p>
            </div>
            <Switch v-model:checked="appEnabled" />
          </div>
          <div class="setting-item">
            <div>
              <h3>短信提醒</h3>
              <p>在离开平台时也能看到高风险通知。</p>
            </div>
            <Switch v-model:checked="smsEnabled" />
          </div>
          <div class="setting-item">
            <div>
              <h3>语音提醒</h3>
              <p>适合高风险夜间场景的补充通知。</p>
            </div>
            <Switch v-model:checked="voiceEnabled" />
          </div>
        </Card>
      </Col>
      <Col :lg="14" :span="24">
        <Card class="template-card" :bordered="false" title="常用提醒文案">
          <Space direction="vertical" style="width: 100%">
            <div v-for="(item, index) in templates" :key="item" class="template-item">
              <div class="template-head">
                <Tag color="blue">模板 {{ index + 1 }}</Tag>
                <Button size="small">使用</Button>
              </div>
              <Input :value="item" readonly />
            </div>
          </Space>
          <div class="template-note">
            <p>当前版本先提供文案配置展示，后续可继续接入编辑、保存和远程发送。</p>
          </div>
        </Card>
      </Col>
    </Row>
  </div>
</template>

<style scoped>
.family-settings-page {
  min-height: 100%;
  padding: 24px;
  background:
    radial-gradient(circle at top right, rgba(225, 29, 72, 0.1), transparent 28%),
    linear-gradient(180deg, #fff8fa 0%, #fff1f5 100%);
}

.hero-panel,
.setting-card,
.template-card {
  border: 1px solid rgba(244, 63, 94, 0.14);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 16px 36px rgba(136, 19, 55, 0.08);
}

.hero-panel {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  padding: 28px 30px;
}

.eyebrow {
  margin: 0 0 12px;
  color: #e11d48;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.08em;
}

h1 {
  margin: 0;
  color: #881337;
  font-size: 34px;
}

.description {
  margin: 16px 0 0;
  color: #9f1239;
  line-height: 1.8;
}

.hero-note {
  max-width: 280px;
  padding: 18px;
  border-radius: 20px;
  background: #fff1f2;
  color: #9f1239;
  line-height: 1.8;
}

.content-row {
  margin-top: 18px;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 16px 0;
  border-bottom: 1px solid rgba(244, 63, 94, 0.12);
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-item h3,
.template-note p {
  margin: 0;
  color: #881337;
}

.setting-item p {
  margin: 8px 0 0;
  color: #9f1239;
  line-height: 1.8;
}

.template-item {
  padding: 16px;
  border-radius: 18px;
  background: #fff7f9;
}

.template-head {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
}

.template-note {
  margin-top: 16px;
  color: #9f1239;
}

@media (max-width: 768px) {
  .family-settings-page {
    padding: 16px;
  }

  .hero-panel,
  .setting-item,
  .template-head {
    flex-direction: column;
  }

  h1 {
    font-size: 28px;
  }
}
</style>
