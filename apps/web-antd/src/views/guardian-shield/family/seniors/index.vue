<script lang="ts" setup>
import { computed, onMounted, reactive, ref } from 'vue';

import {
  Button,
  Card,
  Col,
  Input,
  Row,
  Select,
  Space,
  Tag,
} from 'ant-design-vue';

import {
  getBindingListApi,
  getRiskAlertListApi,
  type RiskAlertItem,
} from '#/api';

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

const loading = ref(false);
const sourceRows = ref<SeniorItem[]>([]);

const filters = reactive({
  keyword: '',
  riskLevel: undefined as string | undefined,
});

const rows = computed(() =>
  sourceRows.value.filter((item) => {
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

function buildBindStatus(authorizedAt: string) {
  const authorized = new Date(authorizedAt).getTime();
  if (Number.isNaN(authorized)) {
    return '已绑定';
  }
  const diffDays = Math.max(
    Math.floor((Date.now() - authorized) / (1000 * 60 * 60 * 24)),
    0,
  );
  return `已绑定 ${diffDays} 天`;
}

function buildRiskSummary(item?: {
  hitReason: string;
  riskLevel: SeniorItem['riskLevel'];
  status: 'handled' | 'pending';
}) {
  if (!item) {
    return '当前暂无风险事件，可继续保持日常关注。';
  }
  if (item.status === 'pending') {
    return `最近有${getRiskMeta(item.riskLevel).text}事件，建议优先电话核实。`;
  }
  return `最近风险事件已处理，原因：${item.hitReason}`;
}

async function loadRows() {
  loading.value = true;
  try {
    const [bindings, alerts] = await Promise.all([
      getBindingListApi(),
      getRiskAlertListApi({ page: 1, pageSize: 50 }),
    ]);
    const latestAlertMap = new Map<string, RiskAlertItem>(
      alerts.items.map((item: RiskAlertItem) => [item.elderName, item] as const),
    );
    sourceRows.value = bindings.map((item) => {
      const latestAlert = latestAlertMap.get(item.elderName);
      return {
        bindStatus: buildBindStatus(item.authorizedAt),
        id: item.elderUserId,
        lastAlert: latestAlert?.occurredAt || '暂无风险告警',
        latestAlertTitle: latestAlert?.title || '近期暂无风险提醒',
        name: item.elderName,
        relation: item.relationshipType,
        riskLevel: latestAlert?.riskLevel || 'low',
        riskSummary: buildRiskSummary(latestAlert),
      } satisfies SeniorItem;
    });
  } finally {
    loading.value = false;
  }
}

function getRiskMeta(level: SeniorItem['riskLevel']) {
  if (level === 'high') return { color: 'red', text: '高风险' };
  if (level === 'medium') return { color: 'orange', text: '中风险' };
  return { color: 'green', text: '低风险' };
}

onMounted(() => {
  void loadRows();
});
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

    <Row v-if="rows.length" :gutter="[16, 16]" class="list-row">
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
    <Card v-else class="empty-card" :bordered="false" :loading="loading">
      当前暂无已绑定老人数据。
    </Card>
  </div>
</template>

<style scoped>
.family-seniors-page {
  min-height: 100%;
  padding: 24px;
  background:
    radial-gradient(circle at top right, rgb(220 38 38 / 10%), transparent 28%),
    linear-gradient(180deg, #fff8f8 0%, #fff1f2 100%);
}

.hero-panel,
.filter-card,
.senior-card,
.empty-card {
  background: rgb(255 255 255 / 96%);
  border: 1px solid rgb(244 63 94 / 14%);
  border-radius: 24px;
  box-shadow: 0 16px 36px rgb(136 19 55 / 8%);
}

.hero-panel {
  display: flex;
  gap: 20px;
  justify-content: space-between;
  padding: 28px 30px;
}

.eyebrow {
  margin: 0 0 12px;
  font-size: 13px;
  font-weight: 700;
  color: #e11d48;
  letter-spacing: 0.08em;
}

h1 {
  margin: 0;
  font-size: 34px;
  color: #881337;
}

.description {
  margin: 16px 0 0;
  line-height: 1.8;
  color: #9f1239;
}

.hero-note {
  max-width: 280px;
  padding: 18px;
  line-height: 1.8;
  color: #9f1239;
  background: #fff1f2;
  border-radius: 20px;
}

.filter-card,
.list-row {
  margin-top: 18px;
}

.card-head {
  display: flex;
  gap: 16px;
  justify-content: space-between;
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
  padding: 18px;
  margin-top: 16px;
  background: #fff7f8;
  border-radius: 18px;
}

.warning {
  background: #fff1f2;
}

.label {
  margin: 0;
  font-weight: 700;
  color: #be123c;
}

.value {
  margin: 10px 0 0;
  font-size: 17px;
  line-height: 1.8;
  color: #881337;
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
