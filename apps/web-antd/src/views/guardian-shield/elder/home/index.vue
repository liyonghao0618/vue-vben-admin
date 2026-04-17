<script lang="ts" setup>
import { computed, onMounted, ref } from 'vue';

import { Button, Card, Col, Empty, Row, Skeleton, Space, Tag } from 'ant-design-vue';
import { useRouter } from 'vue-router';

import {
  getAccessibilitySettingsApi,
  getBindingListApi,
  getRiskAlertListApi,
  type AccessibilitySettings,
  type BindingItem,
  type RiskAlertItem,
} from '#/api';

defineOptions({ name: 'ElderHome' });

const router = useRouter();
const loading = ref(false);
const alerts = ref<RiskAlertItem[]>([]);
const bindings = ref<BindingItem[]>([]);
const settings = ref<AccessibilitySettings | null>(null);

const latestAlert = computed(() => alerts.value[0] ?? null);
const highRiskCount = computed(
  () => alerts.value.filter((item) => item.riskLevel === 'high').length,
);
const pendingCount = computed(
  () => alerts.value.filter((item) => item.status === 'pending').length,
);
const activeClassName = computed(() => [
  settings.value?.highContrast ? 'is-high-contrast' : '',
  settings.value?.fontScale === 'x-large'
    ? 'font-xl'
    : settings.value?.fontScale === 'large'
      ? 'font-lg'
      : 'font-normal',
].join(' '));
const voiceTip = computed(() => {
  if (!settings.value?.voiceAssistant) {
    return '当前未开启语音辅助，可在适老设置中开启朗读。';
  }
  return `语音辅助已开启，当前语速为${settings.value.voiceSpeed === 'slow' ? '慢速' : settings.value.voiceSpeed === 'fast' ? '快速' : '正常'}。`;
});

async function loadPageData() {
  loading.value = true;
  try {
    const [alertData, bindingData, settingData] = await Promise.all([
      getRiskAlertListApi({ page: 1, pageSize: 6 }),
      getBindingListApi(),
      getAccessibilitySettingsApi(),
    ]);
    alerts.value = alertData.items;
    bindings.value = bindingData;
    settings.value = settingData;
  } finally {
    loading.value = false;
  }
}

function goTo(path: string) {
  void router.push(path);
}

onMounted(() => {
  void loadPageData();
});
</script>

<template>
  <div class="elder-home-page" :class="activeClassName">
    <section class="hero-panel">
      <div>
        <p class="eyebrow">老年端 / 首页</p>
        <h1>{{ latestAlert?.riskLevel === 'high' ? '先别慌，先不要转账' : '今天先看这三件事' }}</h1>
        <p class="description">
          围绕“有没有危险、该先联系谁、现在要做什么”三件事组织首页信息，让老人进入系统后不用翻页面就能先做正确动作。
        </p>
      </div>
      <div class="hero-note">
        <strong>今日提醒</strong>
        <span>{{ voiceTip }}</span>
      </div>
    </section>

    <Skeleton active :loading="loading" :paragraph="{ rows: 8 }">
      <Row :gutter="[16, 16]" class="summary-row">
        <Col :lg="8" :span="24">
          <Card class="summary-card" :bordered="false">
            <p class="summary-title">风险提醒</p>
            <strong class="summary-value">{{ alerts.length }}</strong>
            <p class="summary-desc">其中高风险 {{ highRiskCount }} 条，待处理 {{ pendingCount }} 条。</p>
          </Card>
        </Col>
        <Col :lg="8" :span="24">
          <Card class="summary-card" :bordered="false">
            <p class="summary-title">已绑定家人</p>
            <strong class="summary-value">{{ bindings.length }}</strong>
            <p class="summary-desc">
              {{
                bindings.find((item) => item.isEmergencyContact)?.familyName
                  ? `紧急联系人：${bindings.find((item) => item.isEmergencyContact)?.familyName}`
                  : '暂未设置紧急联系人'
              }}
            </p>
          </Card>
        </Col>
        <Col :lg="8" :span="24">
          <Card class="summary-card" :bordered="false">
            <p class="summary-title">显示模式</p>
            <strong class="summary-value">
              {{ settings?.fontScale === 'x-large' ? '超大字' : settings?.fontScale === 'large' ? '大字号' : '标准' }}
            </strong>
            <p class="summary-desc">
              {{ settings?.highContrast ? '已开启高对比度，页面会更清楚。' : '当前为普通对比度，可在设置页调整。' }}
            </p>
          </Card>
        </Col>
      </Row>

      <Row :gutter="[16, 16]">
        <Col :lg="15" :span="24">
          <Card class="focus-card" :bordered="false" title="当前最需要注意">
            <template v-if="latestAlert">
              <div class="alert-head">
                <div>
                  <h2>{{ latestAlert.title }}</h2>
                  <p>{{ latestAlert.occurredAt }} · {{ latestAlert.elderName }}</p>
                </div>
                <Space wrap>
                  <Tag :color="latestAlert.riskLevel === 'high' ? 'red' : latestAlert.riskLevel === 'medium' ? 'orange' : 'green'">
                    {{ latestAlert.riskLevel === 'high' ? '高风险' : latestAlert.riskLevel === 'medium' ? '中风险' : '低风险' }}
                  </Tag>
                  <Tag color="blue">风险分 {{ latestAlert.riskScore }}</Tag>
                </Space>
              </div>
              <div class="focus-grid">
                <div class="focus-block">
                  <p class="block-label">为什么提醒</p>
                  <p>{{ latestAlert.hitReason }}</p>
                </div>
                <div class="focus-block">
                  <p class="block-label">现在怎么做</p>
                  <p>{{ latestAlert.advice }}</p>
                </div>
                <div class="focus-block">
                  <p class="block-label">可疑内容</p>
                  <p>{{ latestAlert.contentPreview }}</p>
                </div>
              </div>
            </template>
            <Empty v-else description="当前暂无风险提醒" />
          </Card>
        </Col>
        <Col :lg="9" :span="24">
          <Card class="action-card" :bordered="false" title="马上操作">
            <Space direction="vertical" style="width: 100%">
              <Button block size="large" type="primary" @click="goTo('/elder/alerts')">查看风险提醒</Button>
              <Button block size="large" danger @click="goTo('/elder/help')">一键求助</Button>
              <Button block size="large" @click="goTo('/elder/family-binding')">联系家人</Button>
              <Button block size="large" @click="goTo('/elder/settings')">调整适老设置</Button>
            </Space>
          </Card>
        </Col>
      </Row>
    </Skeleton>
  </div>
</template>

<style scoped>
.elder-home-page {
  min-height: 100%;
  padding: 24px;
  color: #7c2d12;
  background:
    radial-gradient(circle at top right, rgb(217 119 6 / 12%), transparent 30%),
    linear-gradient(180deg, #fffaf2 0%, #fff4e6 100%);
}

.hero-panel,
.summary-card,
.focus-card,
.action-card {
  background: rgb(255 255 255 / 96%);
  border: 1px solid rgb(245 158 11 / 18%);
  border-radius: 24px;
  box-shadow: 0 16px 36px rgb(124 45 18 / 8%);
}

.hero-panel {
  display: flex;
  gap: 20px;
  justify-content: space-between;
  padding: 28px 30px;
  margin-bottom: 18px;
}

.eyebrow {
  margin: 0 0 12px;
  font-size: 13px;
  font-weight: 700;
  color: #d97706;
  letter-spacing: 0.08em;
}

h1,
h2 {
  margin: 0;
}

h1 {
  font-size: 34px;
}

.description,
.summary-desc,
.hero-note,
.focus-block p:last-child,
.alert-head p {
  line-height: 1.8;
  color: #7c4a2d;
}

.hero-note {
  max-width: 280px;
  padding: 18px;
  background: #fff7ed;
  border-radius: 20px;
}

.summary-title,
.block-label {
  margin: 0 0 10px;
  font-weight: 700;
  color: #b45309;
}

.summary-value {
  font-size: 34px;
}

.summary-row {
  margin-bottom: 18px;
}

.alert-head,
.focus-grid {
  display: grid;
  gap: 16px;
}

.alert-head {
  margin-bottom: 18px;
}

.focus-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.focus-block {
  padding: 18px;
  background: #fff8ef;
  border-radius: 18px;
}

.font-lg {
  font-size: 18px;
}

.font-xl {
  font-size: 20px;
}

.is-high-contrast {
  color: #2f1300;
  background:
    radial-gradient(circle at top right, rgb(146 64 14 / 20%), transparent 30%),
    linear-gradient(180deg, #fff7db 0%, #ffe9b5 100%);
}

.is-high-contrast .hero-panel,
.is-high-contrast .summary-card,
.is-high-contrast .focus-card,
.is-high-contrast .action-card {
  border-color: rgb(146 64 14 / 35%);
  box-shadow: 0 18px 40px rgb(120 53 15 / 12%);
}

@media (max-width: 768px) {
  .elder-home-page {
    padding: 16px;
  }

  .hero-panel,
  .focus-grid {
    grid-template-columns: 1fr;
  }

  .hero-panel {
    flex-direction: column;
  }

  h1 {
    font-size: 28px;
  }
}
</style>
