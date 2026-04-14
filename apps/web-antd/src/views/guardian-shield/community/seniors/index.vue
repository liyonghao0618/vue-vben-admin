<script lang="ts" setup>
import { computed, reactive } from 'vue';

import { Button, Card, Col, Input, Row, Select, Space, Tag } from 'ant-design-vue';

defineOptions({ name: 'CommunitySeniors' });

interface FocusSeniorItem {
  collaboration: string;
  elderName: string;
  followUpStatus: string;
  id: string;
  labels: string[];
  riskLevel: 'high' | 'low' | 'medium';
}

const sourceRows: FocusSeniorItem[] = [
  {
    collaboration: '已同步家属李静，建议 2 小时内电话回访。',
    elderName: '王阿姨',
    followUpStatus: '待首次回访',
    id: 'CS-1',
    labels: ['独居', '高频短信', '需重点核查'],
    riskLevel: 'high',
  },
  {
    collaboration: '社区民警与家属联合跟进，等待核实结果。',
    elderName: '周奶奶',
    followUpStatus: '联动处理中',
    id: 'CS-2',
    labels: ['高龄', '通话高风险'],
    riskLevel: 'high',
  },
  {
    collaboration: '建议下次宣教时重点提醒验证码骗局。',
    elderName: '孙大爷',
    followUpStatus: '已电话回访',
    id: 'CS-3',
    labels: ['需宣教', '退款类风险'],
    riskLevel: 'medium',
  },
  {
    collaboration: '家属已确认暂无转账行为，待二次电话确认。',
    elderName: '赵桂兰',
    followUpStatus: '待复核',
    id: 'CS-4',
    labels: ['低风险', '熟人冒充'],
    riskLevel: 'low',
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
      [item.elderName, item.followUpStatus, item.labels.join(' '), item.id]
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

function getRiskMeta(level: FocusSeniorItem['riskLevel']) {
  if (level === 'high') return { color: 'red', text: '高风险' };
  if (level === 'medium') return { color: 'orange', text: '中风险' };
  return { color: 'green', text: '低风险' };
}
</script>

<template>
  <div class="community-seniors-page">
    <section class="hero-panel">
      <div>
        <p class="eyebrow">社区端 / 重点对象</p>
        <h1>重点老人</h1>
        <p class="description">
          汇总辖区内需要重点关注的老人，查看风险标签、回访状态和当前协同情况，便于安排走访和宣教。
        </p>
      </div>
      <div class="hero-note">
        <strong>工作提示</strong>
        <span>高风险对象优先电话回访，必要时联动家属和社区民警。</span>
      </div>
    </section>

    <Card class="filter-card" :bordered="false">
      <Space wrap :size="12">
        <Input
          v-model:value="filters.keyword"
          allow-clear
          placeholder="搜索老人、标签或回访状态"
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
              <h3>{{ item.elderName }}</h3>
              <p>{{ item.id }} · {{ item.followUpStatus }}</p>
            </div>
            <Tag :color="getRiskMeta(item.riskLevel).color">
              {{ getRiskMeta(item.riskLevel).text }}
            </Tag>
          </div>
          <div class="tag-row">
            <Tag v-for="tag in item.labels" :key="tag" color="blue">{{ tag }}</Tag>
          </div>
          <div class="info-block">
            <p class="label">协同信息</p>
            <p class="value">{{ item.collaboration }}</p>
          </div>
        </Card>
      </Col>
    </Row>
  </div>
</template>

<style scoped>
.community-seniors-page {
  min-height: 100%;
  padding: 24px;
  background:
    radial-gradient(circle at top right, rgba(16, 185, 129, 0.12), transparent 28%),
    linear-gradient(180deg, #f6fffb 0%, #edfff7 100%);
}

.hero-panel,
.filter-card,
.senior-card {
  border: 1px solid rgba(16, 185, 129, 0.14);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 16px 36px rgba(6, 95, 70, 0.08);
}

.hero-panel {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  padding: 28px 30px;
}

.eyebrow {
  margin: 0 0 12px;
  color: #059669;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.08em;
}

h1 {
  margin: 0;
  color: #065f46;
  font-size: 34px;
}

.description {
  margin: 16px 0 0;
  color: #047857;
  line-height: 1.8;
}

.hero-note {
  max-width: 280px;
  padding: 18px;
  border-radius: 20px;
  background: #ecfdf5;
  color: #047857;
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
  color: #065f46;
}

.card-head p {
  margin: 8px 0 0;
  color: #047857;
}

.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 14px;
}

.info-block {
  margin-top: 16px;
  padding: 18px;
  border-radius: 18px;
  background: #f0fdf4;
}

.label {
  margin: 0;
  color: #047857;
  font-weight: 700;
}

.value {
  margin: 10px 0 0;
  color: #065f46;
  line-height: 1.8;
}

@media (max-width: 768px) {
  .community-seniors-page {
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
