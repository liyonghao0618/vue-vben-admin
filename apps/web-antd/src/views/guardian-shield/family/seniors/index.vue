<script lang="ts" setup>
import { computed, reactive } from 'vue';

import { Button, Card, Col, Input, Row, Select, Space, Tag } from 'ant-design-vue';

defineOptions({ name: 'FamilySeniors' });

interface SeniorItem {
  bindStatus: string;
  id: string;
  lastAlert: string;
  latestAlertTitle: string;
  name: string;
  relation: string;
  riskLevel: 'high' | 'low' | 'medium';
  riskSummary: string;
}

const sourceRows: SeniorItem[] = [
  {
    bindStatus: '已绑定 128 天',
    id: 'ELD-1',
    lastAlert: '2026-04-14 09:12',
    latestAlertTitle: '疑似冒充医保短信',
    name: '王阿姨',
    relation: '母亲',
    riskLevel: 'high',
    riskSummary: '今日出现高风险短信，建议优先电话核实。',
  },
  {
    bindStatus: '已绑定 96 天',
    id: 'ELD-2',
    lastAlert: '2026-04-14 08:45',
    latestAlertTitle: '疑似冒充公检法来电',
    name: '周奶奶',
    relation: '外婆',
    riskLevel: 'high',
    riskSummary: '正在处理中，社区已跟进。',
  },
  {
    bindStatus: '已绑定 54 天',
    id: 'ELD-3',
    lastAlert: '2026-04-13 18:20',
    latestAlertTitle: '疑似退款验证码套取',
    name: '孙大爷',
    relation: '父亲',
    riskLevel: 'medium',
    riskSummary: '已完成首次提醒，建议持续关注。',
  },
  {
    bindStatus: '已绑定 41 天',
    id: 'ELD-4',
    lastAlert: '2026-04-12 16:36',
    latestAlertTitle: '疑似熟人冒充来电',
    name: '赵桂兰',
    relation: '姑妈',
    riskLevel: 'low',
    riskSummary: '当前风险较低，可结合通话记录复查。',
  },
];

const filters = reactive({
  keyword: '',
  riskLevel: undefined as string | undefined,
});

const rows = computed(() =>
  sourceRows.filter((item) => {
    const hitKeyword =
      !filters.keyword ||
      [item.name, item.relation, item.latestAlertTitle, item.id]
        .join(' ')
        .toLowerCase()
        .includes(filters.keyword.toLowerCase());
    const hitRisk = !filters.riskLevel || item.riskLevel === filters.riskLevel;
    return hitKeyword && hitRisk;
  }),
);

function resetFilters() {
  filters.keyword = '';
  filters.riskLevel = undefined;
}

function getRiskMeta(level: SeniorItem['riskLevel']) {
  if (level === 'high') return { color: 'red', text: '高风险' };
  if (level === 'medium') return { color: 'orange', text: '中风险' };
  return { color: 'green', text: '低风险' };
}
</script>

<template>
  <div class="family-seniors-page">
    <section class="hero-panel">
      <div>
        <p class="eyebrow">子女端 / 监护对象</p>
        <h1>老人列表</h1>
        <p class="description">
          这里集中查看已绑定老人、当前风险状态和最近一次告警，方便家属快速确认谁需要优先联系。
        </p>
      </div>
      <div class="hero-note">
        <strong>当前关注</strong>
        <span>高风险对象优先联系，不确定时先查看风险详情页。</span>
      </div>
    </section>

    <Card class="filter-card" :bordered="false">
      <Space wrap :size="12">
        <Input
          v-model:value="filters.keyword"
          allow-clear
          placeholder="搜索老人姓名、关系或最近告警"
          style="width: 260px"
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
        <Button @click="resetFilters">重置</Button>
      </Space>
    </Card>

    <Row :gutter="[16, 16]" class="list-row">
      <Col v-for="item in rows" :key="item.id" :lg="12" :span="24">
        <Card class="senior-card" :bordered="false">
          <div class="card-head">
            <div>
              <h3>{{ item.name }}</h3>
              <p>{{ item.relation }} · {{ item.bindStatus }} · {{ item.id }}</p>
            </div>
            <Tag :color="getRiskMeta(item.riskLevel).color">
              {{ getRiskMeta(item.riskLevel).text }}
            </Tag>
          </div>
          <div class="info-block">
            <p class="label">最近告警</p>
            <p class="value">{{ item.latestAlertTitle }}</p>
            <p class="subline">{{ item.lastAlert }}</p>
          </div>
          <div class="info-block warning">
            <p class="label">风险状态</p>
            <p class="value">{{ item.riskSummary }}</p>
          </div>
        </Card>
      </Col>
    </Row>
  </div>
</template>

<style scoped>
.family-seniors-page {
  min-height: 100%;
  padding: 24px;
  background:
    radial-gradient(circle at top right, rgba(220, 38, 38, 0.1), transparent 28%),
    linear-gradient(180deg, #fff8f8 0%, #fff1f2 100%);
}

.hero-panel,
.filter-card,
.senior-card {
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

.filter-card,
.list-row {
  margin-top: 18px;
}

.card-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
}

.card-head h3 {
  margin: 0;
  color: #881337;
}

.card-head p,
.subline {
  margin: 8px 0 0;
  color: #9f1239;
}

.info-block {
  margin-top: 16px;
  padding: 18px;
  border-radius: 18px;
  background: #fff7f8;
}

.warning {
  background: #fff1f2;
}

.label {
  margin: 0;
  color: #be123c;
  font-weight: 700;
}

.value {
  margin: 10px 0 0;
  color: #881337;
  font-size: 17px;
  line-height: 1.8;
}

@media (max-width: 768px) {
  .family-seniors-page {
    padding: 16px;
  }

  .hero-panel,
  .card-head {
    flex-direction: column;
  }

  h1 {
    font-size: 28px;
  }
}
</style>
