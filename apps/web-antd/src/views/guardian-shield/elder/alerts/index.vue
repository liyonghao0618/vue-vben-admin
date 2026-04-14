<script lang="ts" setup>
import { computed, onMounted, reactive, ref } from 'vue';

import { Button, Card, Col, List, Row, Select, Space, Tag } from 'ant-design-vue';
import { useRouter } from 'vue-router';

import { getRiskAlertListApi } from '#/api';
import type { RiskAlertItem } from '#/api';

defineOptions({ name: 'ElderAlerts' });

const router = useRouter();
const loading = ref(false);
const alerts = ref<RiskAlertItem[]>([]);
const total = ref(0);

const filters = reactive({
  page: 1,
  pageSize: 5,
  riskLevel: undefined as string | undefined,
  sourceType: undefined as string | undefined,
  status: undefined as string | undefined,
});

const riskColorMap: Record<RiskAlertItem['riskLevel'], string> = {
  high: 'red',
  low: 'green',
  medium: 'orange',
};

const riskTextMap: Record<RiskAlertItem['riskLevel'], string> = {
  high: '高风险',
  low: '低风险',
  medium: '中风险',
};

const sourceTextMap: Record<RiskAlertItem['sourceType'], string> = {
  call: '通话识别',
  sms: '短信识别',
};

const statusTextMap: Record<RiskAlertItem['status'], string> = {
  handled: '已处理',
  pending: '待处理',
};

const primaryAlert = computed(() => alerts.value[0] ?? null);

const summaryCards = computed(() => {
  const highRiskCount = alerts.value.filter(
    (item) => item.riskLevel === 'high',
  ).length;
  const pendingCount = alerts.value.filter(
    (item) => item.status === 'pending',
  ).length;
  const smsCount = alerts.value.filter((item) => item.sourceType === 'sms').length;

  return [
    {
      title: '当前告警',
      value: `${total.value}`,
      description: '展示短信与通话文本识别后的风险提醒结果。',
    },
    {
      title: '高风险事件',
      value: `${highRiskCount}`,
      description: '需要优先提醒本人并联动家属、社区。',
    },
    {
      title: '待处理提醒',
      value: `${pendingCount}`,
      description: '用于后续串联通知与处置闭环。',
    },
    {
      title: '短信类事件',
      value: `${smsCount}`,
      description: '当前版本优先覆盖链接诱导和验证码套取。',
    },
  ];
});

const quickActions = computed(() => {
  const currentAlert = primaryAlert.value;
  if (!currentAlert) {
    return [
      '看到陌生链接先不要点开',
      '涉及转账先停下来问家人',
      '拿不准时先去一键求助页',
    ];
  }
  return [
    currentAlert.advice,
    currentAlert.contactSuggestion,
    '如果对方一直催促，请立刻挂断电话或删除短信。',
  ];
});

async function loadAlerts() {
  loading.value = true;
  try {
    const data = await getRiskAlertListApi({
      page: filters.page,
      pageSize: filters.pageSize,
      riskLevel: filters.riskLevel,
      sourceType: filters.sourceType,
      status: filters.status,
    });

    alerts.value = data.items;
    total.value = data.total;
  } finally {
    loading.value = false;
  }
}

function handleSearch() {
  filters.page = 1;
  void loadAlerts();
}

function handleReset() {
  filters.page = 1;
  filters.pageSize = 5;
  filters.riskLevel = undefined;
  filters.sourceType = undefined;
  filters.status = undefined;
  void loadAlerts();
}

function handlePageChange(page: number, pageSize: number) {
  filters.page = page;
  filters.pageSize = pageSize;
  void loadAlerts();
}

function getRiskColor(level: RiskAlertItem['riskLevel']) {
  return riskColorMap[level];
}

function getRiskLabel(level: RiskAlertItem['riskLevel']) {
  return riskTextMap[level];
}

function getSourceLabel(type: RiskAlertItem['sourceType']) {
  return sourceTextMap[type];
}

function getStatusLabel(status: RiskAlertItem['status']) {
  return statusTextMap[status];
}

function goToHelpPage() {
  void router.push('/elder/help');
}

function goToFamilyBindingPage() {
  void router.push('/elder/family-binding');
}

onMounted(() => {
  void loadAlerts();
});
</script>

<template>
  <div class="elder-alerts-page">
    <section class="hero-panel">
      <div>
        <p class="eyebrow">老年端 / 核心业务</p>
        <h1>风险提醒</h1>
        <p class="description">
          这里会把可疑短信和电话用更直白的方式告诉您“风险有多大、为什么危险、现在该怎么做”，尽量减少判断压力。
        </p>
      </div>
      <div class="hero-note">
        <strong>适老提示</strong>
        <span>看到“高风险”时，请不要转账，不要点链接，先联系家人或社区。</span>
      </div>
    </section>

    <Row v-if="primaryAlert" :gutter="[16, 16]" class="focus-row">
      <Col :lg="16" :span="24">
        <Card class="focus-card" :bordered="false">
          <div class="focus-header">
            <div>
              <p class="focus-label">优先查看</p>
              <h2>{{ primaryAlert.title }}</h2>
              <p class="focus-time">
                {{ primaryAlert.occurredAt }} · {{ getSourceLabel(primaryAlert.sourceType) }}
              </p>
            </div>
            <div class="focus-tags">
              <Tag :color="getRiskColor(primaryAlert.riskLevel)" class="large-tag">
                {{ getRiskLabel(primaryAlert.riskLevel) }}
              </Tag>
              <Tag color="blue" class="large-tag">风险分 {{ primaryAlert.riskScore }}</Tag>
            </div>
          </div>

          <Row :gutter="[16, 16]">
            <Col :md="8" :span="24">
              <div class="focus-block reason-block">
                <p class="focus-block-label">为什么提醒您</p>
                <p class="focus-block-text">{{ primaryAlert.hitReason }}</p>
              </div>
            </Col>
            <Col :md="8" :span="24">
              <div class="focus-block advice-block">
                <p class="focus-block-label">现在这样做</p>
                <p class="focus-block-text">{{ primaryAlert.advice }}</p>
              </div>
            </Col>
            <Col :md="8" :span="24">
              <div class="focus-block preview-block">
                <p class="focus-block-label">识别到的内容</p>
                <p class="focus-block-text">{{ primaryAlert.contentPreview }}</p>
              </div>
            </Col>
          </Row>
        </Card>
      </Col>
      <Col :lg="8" :span="24">
        <Card class="action-card" :bordered="false">
          <p class="action-title">马上处理</p>
          <ul class="action-list">
            <li v-for="item in quickActions" :key="item">{{ item }}</li>
          </ul>
          <div class="action-buttons">
            <Button block size="large" type="primary" @click="goToHelpPage">一键求助</Button>
            <Button block size="large" @click="goToFamilyBindingPage">联系家人</Button>
          </div>
        </Card>
      </Col>
    </Row>

    <Row :gutter="[16, 16]" class="summary-row">
      <Col v-for="item in summaryCards" :key="item.title" :lg="6" :md="12" :span="24">
        <Card class="summary-card" :bordered="false">
          <p class="summary-title">{{ item.title }}</p>
          <strong class="summary-value">{{ item.value }}</strong>
          <p class="summary-desc">{{ item.description }}</p>
        </Card>
      </Col>
    </Row>

    <Card class="filter-card" :bordered="false">
      <Space :size="12" wrap>
        <Select
          v-model:value="filters.sourceType"
          allow-clear
          placeholder="识别来源"
          style="width: 160px"
          :options="[
            { label: '短信识别', value: 'sms' },
            { label: '通话识别', value: 'call' },
          ]"
        />
        <Select
          v-model:value="filters.riskLevel"
          allow-clear
          placeholder="风险等级"
          style="width: 160px"
          :options="[
            { label: '高风险', value: 'high' },
            { label: '中风险', value: 'medium' },
            { label: '低风险', value: 'low' },
          ]"
        />
        <Select
          v-model:value="filters.status"
          allow-clear
          placeholder="处理状态"
          style="width: 160px"
          :options="[
            { label: '待处理', value: 'pending' },
            { label: '已处理', value: 'handled' },
          ]"
        />
        <Button type="primary" @click="handleSearch">筛选</Button>
        <Button @click="handleReset">重置</Button>
      </Space>
    </Card>

    <Card class="list-card" :bordered="false">
      <List
        :data-source="alerts"
        :loading="loading"
        :locale="{ emptyText: '当前筛选条件下暂无风险提醒' }"
        item-layout="vertical"
        :pagination="{
          current: filters.page,
          pageSize: filters.pageSize,
          total,
          onChange: handlePageChange,
        }"
      >
        <template #renderItem="{ item }">
          <List.Item class="alert-item">
            <div class="alert-header">
              <div>
                <h3>{{ item.title }}</h3>
                <p class="alert-time">{{ item.occurredAt }} · {{ getSourceLabel(item.sourceType) }}</p>
              </div>
              <Space wrap>
                <Tag :color="getRiskColor(item.riskLevel)">{{ getRiskLabel(item.riskLevel) }}</Tag>
                <Tag color="blue">风险分 {{ item.riskScore }}</Tag>
                <Tag>{{ getStatusLabel(item.status) }}</Tag>
              </Space>
            </div>

            <Row :gutter="[16, 16]">
              <Col :lg="12" :span="24">
                <div class="info-card">
                  <p class="info-label">看到的内容</p>
                  <p class="info-text">{{ item.contentPreview }}</p>
                </div>
              </Col>
              <Col :lg="12" :span="24">
                <div class="info-card">
                  <p class="info-label">为什么有风险</p>
                  <p class="info-text">{{ item.hitReason }}</p>
                </div>
              </Col>
              <Col :lg="12" :span="24">
                <div class="info-card advice-card">
                  <p class="info-label">建议您这样做</p>
                  <p class="info-text">{{ item.advice }}</p>
                </div>
              </Col>
              <Col :lg="12" :span="24">
                <div class="info-card contact-card">
                  <p class="info-label">联动建议</p>
                  <p class="info-text">{{ item.contactSuggestion }}</p>
                </div>
              </Col>
            </Row>
          </List.Item>
        </template>
      </List>
    </Card>
  </div>
</template>

<style scoped>
.elder-alerts-page {
  min-height: 100%;
  padding: 24px;
  background:
    radial-gradient(circle at top right, rgba(234, 88, 12, 0.14), transparent 28%),
    linear-gradient(180deg, #fffaf5 0%, #fff4eb 100%);
}

.hero-panel,
.focus-card,
.action-card,
.summary-card,
.filter-card,
.list-card,
.info-card {
  border: 1px solid rgba(251, 146, 60, 0.18);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 16px 36px rgba(120, 53, 15, 0.08);
}

.hero-panel {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  padding: 28px 30px;
}

.eyebrow {
  margin: 0 0 12px;
  color: #ea580c;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.08em;
}

h1 {
  margin: 0;
  color: #7c2d12;
  font-size: 34px;
}

.description {
  max-width: 760px;
  margin: 16px 0 0;
  color: #7c4a2d;
  font-size: 16px;
  line-height: 1.8;
}

.hero-note {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-width: 320px;
  padding: 18px;
  border-radius: 20px;
  background: #fff7ed;
  color: #9a3412;
  line-height: 1.8;
}

.summary-row,
.focus-row,
.filter-card,
.list-card {
  margin-top: 18px;
}

.focus-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

.focus-label {
  margin: 0 0 10px;
  color: #c2410c;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.08em;
}

.focus-header h2 {
  margin: 0;
  color: #7c2d12;
  font-size: 30px;
}

.focus-time {
  margin: 10px 0 0;
  color: #9a3412;
  font-size: 16px;
}

.focus-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.large-tag {
  padding: 8px 14px;
  font-size: 16px;
}

.focus-block {
  height: 100%;
  padding: 20px;
  border-radius: 20px;
}

.reason-block {
  background: #fff7ed;
}

.advice-block {
  background: #fffbeb;
}

.preview-block {
  background: #fff;
  border: 1px solid rgba(251, 146, 60, 0.18);
}

.focus-block-label,
.action-title {
  margin: 0;
  color: #c2410c;
  font-size: 16px;
  font-weight: 700;
}

.focus-block-text {
  margin: 12px 0 0;
  color: #7c4a2d;
  font-size: 20px;
  line-height: 1.8;
}

.action-card {
  height: 100%;
  padding: 8px;
}

.action-list {
  margin: 18px 0 0;
  padding-left: 24px;
  color: #7c4a2d;
  font-size: 18px;
  line-height: 1.9;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 20px;
}

.summary-title,
.summary-desc {
  margin: 0;
}

.summary-title {
  color: #9a3412;
  font-size: 15px;
}

.summary-value {
  display: block;
  margin-top: 10px;
  color: #7c2d12;
  font-size: 30px;
}

.summary-desc {
  margin-top: 12px;
  color: #7c4a2d;
  line-height: 1.7;
}

.alert-item {
  padding: 6px 0 20px;
}

.alert-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.alert-header h3 {
  margin: 0;
  color: #7c2d12;
  font-size: 24px;
}

.alert-time {
  margin: 8px 0 0;
  color: #9a3412;
}

.info-card {
  height: 100%;
  padding: 18px;
}

.info-label {
  margin: 0;
  color: #c2410c;
  font-size: 14px;
  font-weight: 700;
}

.info-text {
  margin: 12px 0 0;
  color: #7c4a2d;
  font-size: 16px;
  line-height: 1.9;
}

.advice-card {
  background: #fff7ed;
}

.contact-card {
  background: #fffbeb;
}

@media (max-width: 768px) {
  .elder-alerts-page {
    padding: 16px;
  }

  .hero-panel,
  .focus-header,
  .alert-header {
    flex-direction: column;
  }

  .hero-panel {
    padding: 22px;
  }

  h1 {
    font-size: 28px;
  }

  .focus-header h2 {
    font-size: 26px;
  }

  .alert-header h3 {
    font-size: 22px;
  }

  .hero-note {
    max-width: none;
  }

  .focus-block-text,
  .action-list {
    font-size: 17px;
  }
}
</style>
