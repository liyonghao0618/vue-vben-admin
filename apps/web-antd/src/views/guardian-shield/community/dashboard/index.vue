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

import { getCommunityOverviewApi } from '#/api';
import type {
  CommunityOverviewData,
  CommunityOverviewFocusSenior,
  CommunityOverviewStat,
  CommunityOverviewTrendItem,
  CommunityOverviewWorkorder,
} from '#/api';

defineOptions({ name: 'CommunityDashboard' });

const loading = ref(false);
const overview = ref<CommunityOverviewData | null>(null);

const riskColorMap: Record<CommunityOverviewFocusSenior['riskLevel'], string> =
  {
    high: 'red',
    low: 'green',
    medium: 'orange',
  };
const riskTextMap: Record<CommunityOverviewFocusSenior['riskLevel'], string> = {
  high: '高风险',
  low: '低风险',
  medium: '中风险',
};
const workorderPriorityMap: Record<
  CommunityOverviewWorkorder['priority'],
  { color: string; text: string }
> = {
  high: { color: 'red', text: '高优先级' },
  low: { color: 'green', text: '低优先级' },
  medium: { color: 'orange', text: '中优先级' },
};
const workorderStatusMap: Record<CommunityOverviewWorkorder['status'], string> =
  {
    archived: '已归档',
    processing: '处理中',
    todo: '待处理',
  };

const summaryCards = computed<CommunityOverviewStat[]>(
  () => overview.value?.stats ?? [],
);
const riskTrend = computed<CommunityOverviewTrendItem[]>(
  () => overview.value?.riskTrend ?? [],
);
const focusSeniors = computed<CommunityOverviewFocusSenior[]>(
  () => overview.value?.focusSeniors ?? [],
);
const todoWorkorders = computed<CommunityOverviewWorkorder[]>(
  () => overview.value?.todoWorkorders ?? [],
);

const maxTrendValue = computed(() =>
  Math.max(
    ...riskTrend.value.flatMap((item) => [item.highRisk, item.visits]),
    1,
  ),
);

function getRiskColor(level: CommunityOverviewFocusSenior['riskLevel']) {
  return riskColorMap[level];
}

function getRiskLabel(level: CommunityOverviewFocusSenior['riskLevel']) {
  return riskTextMap[level];
}

function getPriorityMeta(priority: CommunityOverviewWorkorder['priority']) {
  return workorderPriorityMap[priority];
}

function getStatusLabel(status: CommunityOverviewWorkorder['status']) {
  return workorderStatusMap[status];
}

function getTrendBarStyle(value: number, tone: 'alert' | 'visit') {
  return {
    background:
      tone === 'alert'
        ? 'linear-gradient(90deg, #ea580c 0%, #fb923c 100%)'
        : 'linear-gradient(90deg, #0f766e 0%, #5eead4 100%)',
    width: `${Math.max((value / maxTrendValue.value) * 100, 12)}%`,
  };
}

async function loadOverview() {
  loading.value = true;
  try {
    overview.value = await getCommunityOverviewApi();
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  void loadOverview();
});
</script>

<template>
  <div class="community-dashboard-page">
    <section class="hero-panel">
      <div>
        <p class="eyebrow">社区端 / 协同总览</p>
        <h1>辖区总览</h1>
        <p class="description">
          聚合辖区档案规模、高风险事件、重点对象和待办工单，帮助社区值守人员快速判断今天该先回访谁、先处理哪张单。
        </p>
      </div>
      <div class="hero-note">
        <strong>值守建议</strong>
        <span>先查看高风险对象，再跟进待处理工单，最后补录走访和宣教记录。</span>
      </div>
    </section>

    <Skeleton active :loading="loading" :paragraph="{ rows: 10 }">
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
        <Col :lg="11" :span="24">
          <Card
            class="panel-card"
            :bordered="false"
            title="近 7 日风险与回访趋势"
          >
            <div class="trend-list">
              <div v-for="item in riskTrend" :key="item.date" class="trend-row">
                <span class="trend-date">{{ item.date }}</span>
                <div class="trend-content">
                  <div class="trend-item">
                    <span>高风险</span>
                    <div class="trend-track">
                      <div
                        class="trend-bar"
                        :style="getTrendBarStyle(item.highRisk, 'alert')"
                      />
                    </div>
                    <strong>{{ item.highRisk }}</strong>
                  </div>
                  <div class="trend-item">
                    <span>回访</span>
                    <div class="trend-track">
                      <div
                        class="trend-bar"
                        :style="getTrendBarStyle(item.visits, 'visit')"
                      />
                    </div>
                    <strong>{{ item.visits }}</strong>
                  </div>
                </div>
              </div>
            </div>
          </Card>
        </Col>

        <Col :lg="13" :span="24">
          <Card class="panel-card" :bordered="false" title="重点关注老人">
            <List
              v-if="focusSeniors.length"
              :data-source="focusSeniors"
              :locale="{ emptyText: '暂无重点对象' }"
            >
              <template #renderItem="{ item }">
                <List.Item class="focus-item">
                  <div class="focus-header">
                    <div>
                      <h3>{{ item.elderName }}</h3>
                      <p>{{ item.id }} · 最近告警 {{ item.lastAlertAt }}</p>
                    </div>
                    <Tag :color="getRiskColor(item.riskLevel)">{{
                      getRiskLabel(item.riskLevel)
                    }}</Tag>
                  </div>
                  <Space wrap class="tag-row">
                    <Tag v-for="tag in item.tags" :key="tag" color="blue">{{
                      tag
                    }}</Tag>
                  </Space>
                  <p class="focus-advice">{{ item.disposalAdvice }}</p>
                </List.Item>
              </template>
            </List>
            <Empty v-else description="暂无重点对象" />
          </Card>
        </Col>
      </Row>

      <Card
        class="panel-card workorder-card"
        :bordered="false"
        title="待办工单"
      >
        <List
          v-if="todoWorkorders.length"
          :data-source="todoWorkorders"
          :locale="{ emptyText: '暂无待办工单' }"
        >
          <template #renderItem="{ item }">
            <List.Item class="workorder-item">
              <div class="workorder-main">
                <div>
                  <h3>{{ item.reason }}</h3>
                  <p>
                    {{ item.id }} · {{ item.elderName }} · {{ item.assignee }}
                  </p>
                </div>
                <Space wrap>
                  <Tag :color="getPriorityMeta(item.priority).color">
                    {{ getPriorityMeta(item.priority).text }}
                  </Tag>
                  <Tag>{{ getStatusLabel(item.status) }}</Tag>
                </Space>
              </div>
            </List.Item>
          </template>
        </List>
        <Empty v-else description="暂无待办工单" />
      </Card>
    </Skeleton>
  </div>
</template>

<style scoped>
.community-dashboard-page {
  min-height: 100%;
  padding: 24px;
  background:
    radial-gradient(circle at top right, rgb(194 65 12 / 14%), transparent 28%),
    linear-gradient(180deg, #fffaf5 0%, #fff4eb 100%);
}

.hero-panel,
.summary-card,
.panel-card {
  background: rgb(255 255 255 / 95%);
  border: 1px solid rgb(253 186 116 / 80%);
  border-radius: 24px;
  box-shadow: 0 18px 40px rgb(194 65 12 / 10%);
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
  color: #c2410c;
  letter-spacing: 0.08em;
}

h1 {
  margin: 0;
  font-size: 30px;
  color: #7c2d12;
}

.description,
.summary-desc,
.focus-item p,
.workorder-item p {
  line-height: 1.75;
  color: #7c5e4f;
}

.hero-note {
  max-width: 320px;
  padding: 18px 20px;
  color: #9a3412;
  background: linear-gradient(135deg, #fed7aa 0%, #ffedd5 100%);
  border-radius: 20px;
}

.hero-note strong,
.summary-value,
.focus-header h3,
.workorder-main h3 {
  display: block;
  color: #7c2d12;
}

.summary-row {
  margin-bottom: 16px;
}

.summary-title {
  min-height: 46px;
  margin: 0;
  line-height: 1.6;
  color: #9a3412;
}

.summary-value {
  margin-top: 18px;
  font-size: 30px;
}

.summary-desc {
  margin: 12px 0 0;
}

.trend-list {
  display: grid;
  gap: 16px;
}

.trend-row {
  display: grid;
  grid-template-columns: 50px 1fr;
  gap: 12px;
  align-items: start;
}

.trend-date {
  font-weight: 700;
  color: #9a3412;
}

.trend-content {
  display: grid;
  gap: 10px;
}

.trend-item {
  display: grid;
  grid-template-columns: 42px 1fr 24px;
  gap: 10px;
  align-items: center;
  color: #7c2d12;
}

.trend-track {
  height: 12px;
  overflow: hidden;
  background: #ffedd5;
  border-radius: 999px;
}

.trend-bar {
  height: 100%;
  border-radius: 999px;
}

.focus-item,
.workorder-item {
  padding: 8px 0;
}

.focus-header,
.workorder-main {
  display: flex;
  gap: 16px;
  justify-content: space-between;
}

.focus-header h3,
.workorder-main h3 {
  margin: 0;
  font-size: 18px;
}

.focus-header p,
.focus-advice,
.workorder-main p {
  margin: 8px 0 0;
}

.tag-row {
  margin-top: 12px;
}

.workorder-card {
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
  .community-dashboard-page {
    padding: 16px;
  }

  .hero-panel {
    padding: 22px;
  }

  h1 {
    font-size: 26px;
  }

  .focus-header,
  .workorder-main {
    flex-direction: column;
  }
}
</style>
