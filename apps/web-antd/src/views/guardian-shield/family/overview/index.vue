<script lang="ts" setup>
import { computed, onMounted, ref } from 'vue';

import {
  Card,
  Col,
  Empty,
  List,
  Row,
  Skeleton,
  Space,
  Tag,
} from 'ant-design-vue';

import { getFamilyOverviewApi } from '#/api';
import type {
  FamilyOverviewAlertTrendItem,
  FamilyOverviewData,
  FamilyOverviewFocusItem,
  FamilyOverviewRiskDistributionItem,
  FamilyOverviewStat,
} from '#/api';

defineOptions({ name: 'FamilyOverview' });

const loading = ref(false);
const overview = ref<FamilyOverviewData | null>(null);

const riskColorMap: Record<FamilyOverviewFocusItem['riskLevel'], string> = {
  high: 'red',
  low: 'green',
  medium: 'orange',
};
const riskTextMap: Record<FamilyOverviewFocusItem['riskLevel'], string> = {
  high: '高风险',
  low: '低风险',
  medium: '中风险',
};

const summaryCards = computed<FamilyOverviewStat[]>(
  () => overview.value?.stats ?? [],
);
const focusList = computed<FamilyOverviewFocusItem[]>(
  () => overview.value?.focusList ?? [],
);
const alertTrend = computed<FamilyOverviewAlertTrendItem[]>(
  () => overview.value?.alertTrend ?? [],
);
const riskDistribution = computed<FamilyOverviewRiskDistributionItem[]>(
  () => overview.value?.riskDistribution ?? [],
);

const maxTrendTotal = computed(() =>
  Math.max(...alertTrend.value.map((item) => item.total), 1),
);
const maxDistributionCount = computed(() =>
  Math.max(...riskDistribution.value.map((item) => item.count), 1),
);

function getRiskColor(level: FamilyOverviewFocusItem['riskLevel']) {
  return riskColorMap[level];
}

function getRiskLabel(level: FamilyOverviewFocusItem['riskLevel']) {
  return riskTextMap[level];
}

function getTrendBarStyle(total: number) {
  return {
    width: `${Math.max((total / maxTrendTotal.value) * 100, 12)}%`,
  };
}

function getDistributionBarStyle(count: number) {
  return {
    width: `${Math.max((count / maxDistributionCount.value) * 100, 18)}%`,
  };
}

async function loadOverview() {
  loading.value = true;
  try {
    overview.value = await getFamilyOverviewApi();
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  void loadOverview();
});
</script>

<template>
  <div class="family-overview-page">
    <section class="hero-panel">
      <div>
        <p class="eyebrow">子女端 / 核心闭环</p>
        <h1>监护总览</h1>
        <p class="description">
          把已绑定老人、近 7 日风险变化、重点关注对象和待跟进事件放在同一页，方便家属先判断“谁最需要我立刻联系”。
        </p>
      </div>
      <div class="hero-note">
        <strong>跟进顺序</strong>
        <span>先联系高风险且未确认处置的老人，再查看通知记录和风险详情。</span>
      </div>
    </section>

    <Skeleton active :loading="loading" :paragraph="{ rows: 8 }">
      <Row :gutter="[16, 16]" class="summary-row">
        <Col
          v-for="item in summaryCards"
          :key="item.key"
          :lg="6"
          :md="12"
          :span="24"
        >
          <Card class="summary-card" :bordered="false">
            <p class="summary-title">{{ item.description }}</p>
            <strong class="summary-value">{{ item.value }}</strong>
            <p class="summary-desc">{{ item.trend }}</p>
          </Card>
        </Col>
      </Row>

      <Row :gutter="[16, 16]">
        <Col :lg="14" :span="24">
          <Card class="panel-card" :bordered="false" title="重点关注老人">
            <List
              v-if="focusList.length"
              :data-source="focusList"
              :locale="{ emptyText: '暂无重点关注对象' }"
            >
              <template #renderItem="{ item }">
                <List.Item class="focus-item">
                  <div class="focus-header">
                    <div>
                      <h3>{{ item.elderName }}</h3>
                      <p>{{ item.id }} · 最近告警 {{ item.lastAlertAt }}</p>
                    </div>
                    <Space wrap>
                      <Tag :color="getRiskColor(item.riskLevel)">{{
                        getRiskLabel(item.riskLevel)
                      }}</Tag>
                      <Tag>{{ item.currentStatus }}</Tag>
                    </Space>
                  </div>
                  <p class="focus-summary">{{ item.riskSummary }}</p>
                </List.Item>
              </template>
            </List>
            <Empty v-else description="暂无重点关注对象" />
          </Card>
        </Col>

        <Col :lg="10" :span="24">
          <Card class="panel-card" :bordered="false" title="近 7 日风险趋势">
            <div class="chart-list">
              <div
                v-for="item in alertTrend"
                :key="item.date"
                class="chart-row"
              >
                <span class="chart-label">{{ item.date }}</span>
                <div class="chart-track">
                  <div
                    class="chart-bar"
                    :style="getTrendBarStyle(item.total)"
                  />
                </div>
                <strong class="chart-value">{{ item.total }}</strong>
              </div>
            </div>
          </Card>

          <Card
            class="panel-card distribution-card"
            :bordered="false"
            title="风险级别分布"
          >
            <div class="distribution-list">
              <div
                v-for="item in riskDistribution"
                :key="item.label"
                class="distribution-row"
              >
                <span class="distribution-label">{{ item.label }}</span>
                <div class="distribution-track">
                  <div
                    class="distribution-bar"
                    :style="getDistributionBarStyle(item.count)"
                  />
                </div>
                <strong class="distribution-value">{{ item.count }}</strong>
              </div>
            </div>
          </Card>
        </Col>
      </Row>
    </Skeleton>
  </div>
</template>

<style scoped>
.family-overview-page {
  min-height: 100%;
  padding: 24px;
  background:
    radial-gradient(circle at top right, rgb(37 99 235 / 14%), transparent 28%),
    linear-gradient(180deg, #f6f9ff 0%, #eef4ff 100%);
}

.hero-panel,
.summary-card,
.panel-card {
  background: rgb(255 255 255 / 94%);
  border: 1px solid rgb(191 219 254 / 90%);
  border-radius: 24px;
  box-shadow: 0 18px 38px rgb(37 99 235 / 10%);
}

.hero-panel {
  display: flex;
  gap: 24px;
  justify-content: space-between;
  padding: 28px;
  margin-bottom: 16px;
}

.eyebrow {
  margin: 0 0 10px;
  font-size: 13px;
  font-weight: 700;
  color: #2563eb;
  letter-spacing: 0.08em;
}

h1 {
  margin: 0;
  font-size: 30px;
  color: #102a43;
}

.description,
.summary-desc,
.focus-item p {
  line-height: 1.75;
  color: #486581;
}

.hero-note {
  max-width: 320px;
  padding: 18px 20px;
  color: #1d4ed8;
  background: linear-gradient(135deg, #dbeafe 0%, #eff6ff 100%);
  border-radius: 20px;
}

.hero-note strong,
.summary-value,
.focus-header h3,
.chart-value,
.distribution-value {
  display: block;
  color: #102a43;
}

.summary-row {
  margin-bottom: 16px;
}

.summary-card {
  height: 100%;
}

.summary-title {
  min-height: 46px;
  margin: 0;
  line-height: 1.6;
  color: #334e68;
}

.summary-value {
  margin-top: 18px;
  font-size: 30px;
}

.summary-desc {
  margin: 12px 0 0;
}

.panel-card {
  height: 100%;
}

.focus-item {
  padding: 8px 0;
}

.focus-header {
  display: flex;
  gap: 16px;
  justify-content: space-between;
}

.focus-header h3 {
  margin: 0;
  font-size: 18px;
}

.focus-header p,
.focus-summary {
  margin: 8px 0 0;
}

.chart-list,
.distribution-list {
  display: grid;
  gap: 14px;
}

.chart-row,
.distribution-row {
  display: grid;
  grid-template-columns: 56px 1fr 32px;
  gap: 12px;
  align-items: center;
}

.chart-label,
.distribution-label {
  font-weight: 600;
  color: #334e68;
}

.chart-track,
.distribution-track {
  height: 12px;
  overflow: hidden;
  background: #dbeafe;
  border-radius: 999px;
}

.chart-bar,
.distribution-bar {
  height: 100%;
  border-radius: 999px;
}

.chart-bar {
  background: linear-gradient(90deg, #2563eb 0%, #60a5fa 100%);
}

.distribution-bar {
  background: linear-gradient(90deg, #1d4ed8 0%, #93c5fd 100%);
}

.distribution-card {
  margin-top: 16px;
}

@media (max-width: 992px) {
  .hero-panel {
    flex-direction: column;
  }

  .hero-note {
    max-width: none;
  }
}

@media (max-width: 768px) {
  .family-overview-page {
    padding: 16px;
  }

  .hero-panel {
    padding: 22px;
  }

  h1 {
    font-size: 26px;
  }

  .focus-header {
    flex-direction: column;
  }
}
</style>
