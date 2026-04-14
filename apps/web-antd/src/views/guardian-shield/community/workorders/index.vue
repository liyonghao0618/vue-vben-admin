<script lang="ts" setup>
import { computed, onMounted, reactive, ref } from 'vue';

import {
  Button,
  Card,
  Col,
  Empty,
  Input,
  List,
  Modal,
  Row,
  Select,
  Space,
  Tag,
  message,
} from 'ant-design-vue';

import {
  getCommunityWorkorderDetailApi,
  getCommunityWorkorderListApi,
  transitionCommunityWorkorderApi,
} from '#/api';
import type {
  CommunityWorkorderDetail,
  CommunityWorkorderListItem,
} from '#/api';

defineOptions({ name: 'CommunityWorkorders' });

const loading = ref(false);
const rows = ref<CommunityWorkorderListItem[]>([]);
const total = ref(0);
const actionVisible = ref(false);
const detailVisible = ref(false);
const detailLoading = ref(false);
const currentWorkorder = ref<CommunityWorkorderListItem | null>(null);
const currentDetail = ref<CommunityWorkorderDetail | null>(null);

const filters = reactive({
  keyword: '',
  page: 1,
  pageSize: 5,
  priority: undefined as string | undefined,
  status: undefined as string | undefined,
});

const priorityMap: Record<
  CommunityWorkorderListItem['priority'],
  { color: string; text: string }
> = {
  high: { color: 'red', text: '高优先级' },
  medium: { color: 'orange', text: '中优先级' },
  low: { color: 'green', text: '低优先级' },
};

const riskMap: Record<
  CommunityWorkorderListItem['riskLevel'],
  { color: string; text: string }
> = {
  high: { color: 'red', text: '高风险' },
  medium: { color: 'orange', text: '中风险' },
  low: { color: 'green', text: '低风险' },
};

const sourceTextMap: Record<CommunityWorkorderListItem['sourceType'], string> =
  {
    call: '通话识别',
    sms: '短信识别',
  };

const statusTextMap: Record<CommunityWorkorderListItem['status'], string> = {
  archived: '已归档',
  done: '待归档',
  processing: '处理中',
  todo: '待受理',
};

const summaryCards = computed(() => [
  {
    description: '当前筛选条件下的工单总数。',
    title: '工单总数',
    value: `${total.value}`,
  },
  {
    description: '优先需要社区立即介入的事件。',
    title: '高优先级',
    value: `${rows.value.filter((item) => item.priority === 'high').length}`,
  },
  {
    description: '仍在电话回访、联动核查或宣教中的工单。',
    title: '处理中',
    value: `${rows.value.filter((item) => item.status === 'processing').length}`,
  },
  {
    description: '已完成处置、等待归档沉淀的事件。',
    title: '待归档',
    value: `${rows.value.filter((item) => item.status === 'done').length}`,
  },
]);

const noteMap: Record<CommunityWorkorderListItem['status'], string[]> = {
  archived: ['处置结果已确认。', '风险过程已归档留痕。'],
  done: ['已完成核心处置。', '等待补充归档备注。'],
  processing: ['已联系家属。', '正在安排回访或宣教。'],
  todo: ['待社区受理。', '建议优先电话核实老人状态。'],
};

function getPriorityMeta(priority: CommunityWorkorderListItem['priority']) {
  return priorityMap[priority];
}

function getRiskMeta(riskLevel: CommunityWorkorderListItem['riskLevel']) {
  return riskMap[riskLevel];
}

function getSourceLabel(sourceType: CommunityWorkorderListItem['sourceType']) {
  return sourceTextMap[sourceType];
}

function getStatusLabel(status: CommunityWorkorderListItem['status']) {
  return statusTextMap[status];
}

function getNotes(item: CommunityWorkorderListItem) {
  return [
    `${item.createdAt} 创建工单`,
    item.latestProgress,
    ...noteMap[item.status].map(
      (note) => `${getStatusLabel(item.status)}：${note}`,
    ),
  ];
}

async function loadRows() {
  loading.value = true;
  try {
    const data = await getCommunityWorkorderListApi({
      keyword: filters.keyword || undefined,
      page: filters.page,
      pageSize: filters.pageSize,
      priority: filters.priority,
      status: filters.status,
    });
    rows.value = data.items;
    total.value = data.total;
  } finally {
    loading.value = false;
  }
}

function handleSearch() {
  filters.page = 1;
  void loadRows();
}

function handleReset() {
  filters.keyword = '';
  filters.page = 1;
  filters.pageSize = 5;
  filters.priority = undefined;
  filters.status = undefined;
  void loadRows();
}

function handlePageChange(page: number, pageSize: number) {
  filters.page = page;
  filters.pageSize = pageSize;
  void loadRows();
}

onMounted(() => {
  void loadRows();
});

function openTransition(item: CommunityWorkorderListItem) {
  currentWorkorder.value = item;
  actionVisible.value = true;
}

async function openDetail(item: CommunityWorkorderListItem) {
  currentWorkorder.value = item;
  detailVisible.value = true;
  detailLoading.value = true;
  try {
    currentDetail.value = await getCommunityWorkorderDetailApi(item.id);
  } finally {
    detailLoading.value = false;
  }
}

async function completeWorkorder() {
  if (!currentWorkorder.value) return;
  await transitionCommunityWorkorderApi(currentWorkorder.value.id, {
    actionType: 'close',
    disposeMethod: 'phone_visit',
    disposeResult: '已完成回访与宣教提醒。',
    note: '前端发起流转',
    toStatus: 'closed',
  });
  message.success('工单已完成流转');
  actionVisible.value = false;
  await loadRows();
}
</script>

<template>
  <div class="community-workorders-page">
    <section class="hero-panel">
      <div>
        <p class="eyebrow">社区端 / 协同处置</p>
        <h1>风险工单</h1>
        <p class="description">
          当前页面已经接入真实工单数据，支持工单详情、状态流转展示和备注留痕，便于社区完整追踪每次处置。
        </p>
      </div>
      <div class="hero-note">
        <strong>处置提醒</strong>
        <span>高风险工单优先联系家属并核实老人状态，关键节点同步留痕。</span>
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
        <Input
          v-model:value="filters.keyword"
          allow-clear
          placeholder="搜索工单编号、标题、老人或处理人"
          style="width: 280px"
          @press-enter="handleSearch"
        />
        <Select
          v-model:value="filters.priority"
          allow-clear
          placeholder="优先级"
          style="width: 150px"
          :options="[
            { label: '高优先级', value: 'high' },
            { label: '中优先级', value: 'medium' },
            { label: '低优先级', value: 'low' },
          ]"
        />
        <Select
          v-model:value="filters.status"
          allow-clear
          placeholder="状态"
          style="width: 150px"
          :options="[
            { label: '待受理', value: 'todo' },
            { label: '处理中', value: 'processing' },
            { label: '待归档', value: 'done' },
            { label: '已归档', value: 'archived' },
          ]"
        />
        <Button type="primary" @click="handleSearch">查询</Button>
        <Button @click="handleReset">重置</Button>
      </Space>
    </Card>

    <Card class="list-card" :bordered="false">
      <List
        v-if="rows.length"
        :data-source="rows"
        :loading="loading"
        :pagination="{
          current: filters.page,
          pageSize: filters.pageSize,
          total,
          onChange: handlePageChange,
        }"
      >
        <template #renderItem="{ item }">
          <List.Item class="workorder-item">
            <div class="workorder-header">
              <div>
                <h3>{{ item.title }}</h3>
                <p class="subline">
                  {{ item.id }} · {{ item.elderName }} · {{ item.assignee }} ·
                  {{ item.createdAt }}
                </p>
              </div>
              <Space wrap>
                <Tag :color="getPriorityMeta(item.priority).color">
                  {{ getPriorityMeta(item.priority).text }}
                </Tag>
                <Tag :color="getRiskMeta(item.riskLevel).color">
                  {{ getRiskMeta(item.riskLevel).text }}
                </Tag>
                <Tag color="blue">{{ getSourceLabel(item.sourceType) }}</Tag>
                <Tag>{{ getStatusLabel(item.status) }}</Tag>
              </Space>
            </div>

            <Row :gutter="[16, 16]">
              <Col :lg="8" :span="24">
                <div class="info-card">
                  <p class="info-label">工单详情</p>
                  <p class="info-text">{{ item.latestProgress }}</p>
                </div>
              </Col>
              <Col :lg="8" :span="24">
                <div class="info-card action-card">
                  <p class="info-label">状态流转</p>
                  <p class="info-text">{{ getStatusLabel(item.status) }}</p>
                  <p class="info-subtext">当前责任人：{{ item.assignee }}</p>
                  <Button
                    size="small"
                    @click="openDetail(item)"
                    >查看详情</Button
                  >
                  <Button
                    type="primary"
                    size="small"
                    @click="openTransition(item)"
                    >完成流转</Button
                  >
                </div>
              </Col>
              <Col :lg="8" :span="24">
                <div class="info-card">
                  <p class="info-label">备注记录</p>
                  <ul class="note-list">
                    <li v-for="note in getNotes(item)" :key="note">
                      {{ note }}
                    </li>
                  </ul>
                </div>
              </Col>
            </Row>

            <div class="follow-up">
              <p class="info-label">建议动作</p>
              <p class="info-text">{{ item.followUpAction }}</p>
            </div>
          </List.Item>
        </template>
      </List>
      <Empty
        v-else
        :image="Empty.PRESENTED_IMAGE_SIMPLE"
        description="当前条件下暂无工单"
      />
    </Card>

    <Modal
      v-model:open="detailVisible"
      title="工单详情"
      cancel-text="关闭"
      :footer="null"
    >
      <Card :bordered="false" :loading="detailLoading">
        <template v-if="currentDetail">
          <p><strong>工单编号：</strong>{{ currentDetail.workorderNo }}</p>
          <p><strong>老人：</strong>{{ currentDetail.elderName }}</p>
          <p><strong>标题：</strong>{{ currentDetail.title }}</p>
          <p><strong>最新告警：</strong>{{ currentDetail.latestAlertSummary }}</p>
          <p>
            <strong>处置方式：</strong>{{ currentDetail.disposeMethod || '待补充' }}
          </p>
          <p>
            <strong>处置结果：</strong>{{ currentDetail.disposeResult || '待补充' }}
          </p>
          <p><strong>流转记录：</strong></p>
          <ul class="note-list">
            <li v-for="action in currentDetail.actions" :key="action.id">
              {{ action.createdAt }} · {{ action.operatorName }} ·
              {{ action.fromStatus }} -> {{ action.toStatus }}
              <span v-if="action.note"> · {{ action.note }}</span>
            </li>
          </ul>
        </template>
      </Card>
    </Modal>

    <Modal
      v-model:open="actionVisible"
      title="确认工单流转"
      ok-text="完成"
      cancel-text="关闭"
      @ok="completeWorkorder"
    >
      <p>
        将把工单“{{
          currentWorkorder?.title
        }}”流转为完成/归档状态，并写入处置结果。
      </p>
    </Modal>
  </div>
</template>

<style scoped>
.community-workorders-page {
  min-height: 100%;
  padding: 24px;
  background:
    radial-gradient(circle at top right, rgb(194 65 12 / 14%), transparent 28%),
    linear-gradient(180deg, #fffaf7 0%, #fff1e8 100%);
}

.hero-panel,
.summary-card,
.filter-card,
.list-card,
.info-card {
  background: rgb(255 255 255 / 96%);
  border: 1px solid rgb(194 65 12 / 14%);
  border-radius: 24px;
  box-shadow: 0 16px 36px rgb(124 45 18 / 8%);
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
  color: #c2410c;
  letter-spacing: 0.08em;
}

h1 {
  margin: 0;
  font-size: 34px;
  color: #7c2d12;
}

.description {
  margin: 16px 0 0;
  line-height: 1.8;
  color: #7c4a2d;
}

.hero-note {
  max-width: 300px;
  padding: 18px;
  line-height: 1.8;
  color: #9a3412;
  background: #fff7ed;
  border-radius: 20px;
}

.summary-row,
.filter-card,
.list-card {
  margin-top: 18px;
}

.summary-title,
.summary-desc {
  margin: 0;
}

.summary-title {
  color: #9a3412;
}

.summary-value {
  display: block;
  margin-top: 10px;
  font-size: 30px;
  color: #7c2d12;
}

.summary-desc {
  margin-top: 12px;
  line-height: 1.7;
  color: #7c4a2d;
}

.workorder-item {
  padding: 6px 0 20px;
}

.workorder-header {
  display: flex;
  gap: 16px;
  justify-content: space-between;
  margin-bottom: 16px;
}

.workorder-header h3 {
  margin: 0;
  font-size: 24px;
  color: #7c2d12;
}

.subline {
  margin: 8px 0 0;
  color: #9a3412;
}

.info-card {
  height: 100%;
  padding: 18px;
}

.info-label {
  margin: 0;
  font-weight: 700;
  color: #c2410c;
}

.info-text,
.info-subtext {
  margin: 12px 0 0;
  line-height: 1.8;
  color: #7c4a2d;
}

.note-list {
  padding-left: 20px;
  margin: 12px 0 0;
  line-height: 1.8;
  color: #7c4a2d;
}

.action-card {
  background: #fff7ed;
}

.follow-up {
  padding: 18px;
  margin-top: 16px;
  background: #fffbeb;
  border-radius: 18px;
}

@media (max-width: 768px) {
  .community-workorders-page {
    padding: 16px;
  }

  .hero-panel,
  .workorder-header {
    flex-direction: column;
  }

  h1 {
    font-size: 28px;
  }

  .workorder-header h3 {
    font-size: 22px;
  }
}
</style>
