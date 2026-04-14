<script lang="ts" setup>
import type { TableColumnsType } from 'ant-design-vue';

import { computed, onMounted, reactive, ref } from 'vue';

import {
  Button,
  Card,
  Col,
  Row,
  Select,
  Space,
  Table,
  Tag,
} from 'ant-design-vue';

import {
  getFamilyNotificationListApi,
  markFamilyNotificationReadApi,
} from '#/api';
import type { FamilyNotificationItem } from '#/api';

defineOptions({ name: 'FamilyNotifications' });

const loading = ref(false);
const rows = ref<FamilyNotificationItem[]>([]);
const total = ref(0);

const filters = reactive({
  page: 1,
  pageSize: 5,
  readStatus: undefined as string | undefined,
  riskLevel: undefined as string | undefined,
  status: undefined as string | undefined,
});

const riskMap: Record<
  FamilyNotificationItem['riskLevel'],
  { color: string; text: string }
> = {
  high: { color: 'red', text: '高风险' },
  medium: { color: 'orange', text: '中风险' },
  low: { color: 'green', text: '低风险' },
};
const readMap: Record<FamilyNotificationItem['readStatus'], string> = {
  read: '已读',
  unread: '未读',
};
const channelMap: Record<FamilyNotificationItem['channel'], string> = {
  app: '站内提醒',
  sms: '短信',
  voice: '语音通知',
};
const resultMap: Record<FamilyNotificationItem['result'], string> = {
  delivered: '已送达',
  failed: '发送失败',
  processing: '发送中',
};
const statusMap: Record<FamilyNotificationItem['status'], string> = {
  closed: '已关闭',
  follow_up: '跟进中',
  pending: '待处理',
};

const summaryCards = computed(() => [
  {
    title: '通知记录',
    value: `${total.value}`,
    description: '沉淀系统向子女侧发送的高风险提醒记录。',
  },
  {
    title: '未读',
    value: `${rows.value.filter((item) => item.readStatus === 'unread').length}`,
    description: '用于突出尚未查看的风险通知。',
  },
  {
    title: '高风险通知',
    value: `${rows.value.filter((item) => item.riskLevel === 'high').length}`,
    description: '优先推动家属联系老人并同步社区。',
  },
  {
    title: '跟进中',
    value: `${rows.value.filter((item) => item.status === 'follow_up').length}`,
    description: '用于追踪正在处理的风险事件。',
  },
]);

const columns: TableColumnsType<FamilyNotificationItem> = [
  {
    dataIndex: 'relatedAlertTitle',
    key: 'relatedAlertTitle',
    title: '关联事件',
  },
  { dataIndex: 'elderName', key: 'elderName', title: '老人' },
  { dataIndex: 'riskLevel', key: 'riskLevel', title: '风险等级' },
  { dataIndex: 'channel', key: 'channel', title: '通知渠道' },
  { dataIndex: 'notifiedAt', key: 'notifiedAt', title: '通知时间' },
  { dataIndex: 'result', key: 'result', title: '发送结果' },
  { dataIndex: 'status', key: 'status', title: '处置状态' },
  { key: 'actions', title: '操作' },
];

function getRiskMeta(level: FamilyNotificationItem['riskLevel']) {
  return riskMap[level];
}

function getReadLabel(status: FamilyNotificationItem['readStatus']) {
  return readMap[status];
}

function getChannelLabel(channel: FamilyNotificationItem['channel']) {
  return channelMap[channel];
}

function getResultLabel(result: FamilyNotificationItem['result']) {
  return resultMap[result];
}

function getStatusLabel(status: FamilyNotificationItem['status']) {
  return statusMap[status];
}

async function loadRows() {
  loading.value = true;
  try {
    const data = await getFamilyNotificationListApi({
      page: filters.page,
      pageSize: filters.pageSize,
      readStatus: filters.readStatus,
      riskLevel: filters.riskLevel,
      status: filters.status,
    });
    rows.value = data.items;
    total.value = data.total;
  } finally {
    loading.value = false;
  }
}

async function handleMarkRead(notificationId: string) {
  await markFamilyNotificationReadApi(notificationId);
  await loadRows();
}

function handleSearch() {
  filters.page = 1;
  void loadRows();
}

function handleReset() {
  filters.page = 1;
  filters.pageSize = 5;
  filters.readStatus = undefined;
  filters.riskLevel = undefined;
  filters.status = undefined;
  void loadRows();
}

function handleTableChange(page: number, pageSize: number) {
  filters.page = page;
  filters.pageSize = pageSize;
  void loadRows();
}

onMounted(() => {
  void loadRows();
});
</script>

<template>
  <div class="family-notifications-page">
    <section class="hero-panel">
      <div>
        <p class="eyebrow">子女端 / 通知中心</p>
        <h1>通知记录</h1>
        <p class="description">
          当前页面已经接入真实通知记录，可查看通知渠道、送达结果、已读状态和后续跟进状态，并支持直接标记已读。
        </p>
      </div>
    </section>

    <Row :gutter="[16, 16]" class="summary-row">
      <Col
        v-for="item in summaryCards"
        :key="item.title"
        :lg="6"
        :md="12"
        :span="24"
      >
        <Card class="summary-card" :bordered="false">
          <p class="summary-title">{{ item.title }}</p>
          <strong class="summary-value">{{ item.value }}</strong>
          <p class="summary-desc">{{ item.description }}</p>
        </Card>
      </Col>
    </Row>

    <Card class="filter-card" :bordered="false">
      <Space wrap :size="12">
        <Select
          v-model:value="filters.riskLevel"
          allow-clear
          placeholder="风险等级"
          style="width: 150px"
          :options="[
            { label: '高风险', value: 'high' },
            { label: '中风险', value: 'medium' },
            { label: '低风险', value: 'low' },
          ]"
        />
        <Select
          v-model:value="filters.readStatus"
          allow-clear
          placeholder="阅读状态"
          style="width: 150px"
          :options="[
            { label: '未读', value: 'unread' },
            { label: '已读', value: 'read' },
          ]"
        />
        <Select
          v-model:value="filters.status"
          allow-clear
          placeholder="处置状态"
          style="width: 150px"
          :options="[
            { label: '待处理', value: 'pending' },
            { label: '跟进中', value: 'follow_up' },
            { label: '已关闭', value: 'closed' },
          ]"
        />
        <Button type="primary" @click="handleSearch">筛选</Button>
        <Button @click="handleReset">重置</Button>
      </Space>
    </Card>

    <Card class="table-card" :bordered="false">
      <Table
        :columns="columns"
        :data-source="rows"
        :loading="loading"
        row-key="id"
        :pagination="{
          current: filters.page,
          pageSize: filters.pageSize,
          total,
          onChange: handleTableChange,
          onShowSizeChange: handleTableChange,
        }"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'relatedAlertTitle'">
            <div class="event-cell">
              <strong>{{ record.relatedAlertTitle }}</strong>
              <span>{{ record.id }} · {{ record.operatorName }}</span>
            </div>
          </template>
          <template v-else-if="column.key === 'riskLevel'">
            <Space wrap>
              <Tag :color="getRiskMeta(record.riskLevel).color">{{
                getRiskMeta(record.riskLevel).text
              }}</Tag>
              <Tag>{{ getReadLabel(record.readStatus) }}</Tag>
            </Space>
          </template>
          <template v-else-if="column.key === 'channel'">
            <Tag color="blue">{{ getChannelLabel(record.channel) }}</Tag>
          </template>
          <template v-else-if="column.key === 'result'">
            <Tag>{{ getResultLabel(record.result) }}</Tag>
          </template>
          <template v-else-if="column.key === 'status'">
            <Tag color="purple">{{ getStatusLabel(record.status) }}</Tag>
          </template>
          <template v-else-if="column.key === 'actions'">
            <Button
              size="small"
              type="link"
              :disabled="record.readStatus === 'read'"
              @click="handleMarkRead(record.id)"
            >
              {{ record.readStatus === 'read' ? '已读' : '标记已读' }}
            </Button>
          </template>
        </template>
      </Table>
    </Card>
  </div>
</template>

<style scoped>
.family-notifications-page {
  min-height: 100%;
  padding: 24px;
  background:
    radial-gradient(
      circle at top right,
      rgb(147 51 234 / 12%),
      transparent 28%
    ),
    linear-gradient(180deg, #fbf8ff 0%, #f5f3ff 100%);
}

.hero-panel,
.summary-card,
.filter-card,
.table-card {
  background: rgb(255 255 255 / 96%);
  border: 1px solid rgb(147 51 234 / 12%);
  border-radius: 24px;
  box-shadow: 0 16px 36px rgb(88 28 135 / 8%);
}

.hero-panel {
  padding: 28px 30px;
}

.eyebrow {
  margin: 0 0 12px;
  font-size: 13px;
  font-weight: 700;
  color: #7c3aed;
  letter-spacing: 0.08em;
}

h1 {
  margin: 0;
  color: #581c87;
}

.description {
  max-width: 760px;
  margin-top: 16px;
  line-height: 1.8;
  color: #6b21a8;
}

.summary-row,
.filter-card,
.table-card {
  margin-top: 18px;
}

.summary-title {
  margin: 0;
  color: #7c3aed;
}

.summary-value {
  display: block;
  margin-top: 10px;
  font-size: 30px;
  color: #581c87;
}

.summary-desc {
  margin-top: 10px;
  line-height: 1.7;
  color: #6b21a8;
}

.event-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.event-cell strong {
  color: #3b0764;
}

.event-cell span {
  font-size: 13px;
  color: #7e22ce;
}

@media (max-width: 768px) {
  .family-notifications-page {
    padding: 16px;
  }
}
</style>
