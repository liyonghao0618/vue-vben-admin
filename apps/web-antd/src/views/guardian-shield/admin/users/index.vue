<script lang="ts" setup>
import type { TableColumnsType } from 'ant-design-vue';

import type { AdminUserListItem } from '#/api';

import { computed, onMounted, reactive, ref } from 'vue';

import {
  Button,
  Card,
  Col,
  Empty,
  Input,
  Row,
  Select,
  Space,
  Table,
  Tag,
} from 'ant-design-vue';

import { getAdminUserListApi } from '#/api';

defineOptions({ name: 'AdminUsers' });

const loading = ref(false);
const rows = ref<AdminUserListItem[]>([]);
const total = ref(0);

const filters = reactive({
  keyword: '',
  page: 1,
  pageSize: 5,
  role: undefined as string | undefined,
  status: undefined as string | undefined,
});

const roleTextMap: Record<AdminUserListItem['role'], string> = {
  admin: '管理员',
  community: '社区工作人员',
  elder: '老年用户',
  family: '子女用户',
};

const riskColorMap: Record<AdminUserListItem['riskLevel'], string> = {
  high: 'red',
  low: 'green',
  medium: 'orange',
};

const riskTextMap: Record<AdminUserListItem['riskLevel'], string> = {
  high: '高风险',
  low: '低风险',
  medium: '中风险',
};

const statusColorMap: Record<AdminUserListItem['status'], string> = {
  disabled: 'default',
  enabled: 'success',
};

const statusTextMap: Record<AdminUserListItem['status'], string> = {
  disabled: '停用',
  enabled: '启用',
};

const summaryCards = computed(() => {
  const elderCount = rows.value.filter((item) => item.role === 'elder').length;
  const highRiskCount = rows.value.filter(
    (item) => item.riskLevel === 'high',
  ).length;
  const enabledCount = rows.value.filter(
    (item) => item.status === 'enabled',
  ).length;

  return [
    {
      title: '当前列表人数',
      value: `${total.value}`,
      description: '结合筛选条件统计当前可见用户总数。',
    },
    {
      title: '老年用户',
      value: `${elderCount}`,
      description: '第一阶段重点关注适老页面和风险提醒闭环。',
    },
    {
      title: '高风险对象',
      value: `${highRiskCount}`,
      description: '为后续重点关注、工单流转提供基础口径。',
    },
    {
      title: '启用账号',
      value: `${enabledCount}`,
      description: '便于后续叠加停用、重置和审计操作。',
    },
  ];
});

const columns: TableColumnsType<AdminUserListItem> = [
  {
    dataIndex: 'name',
    key: 'name',
    title: '用户信息',
  },
  {
    dataIndex: 'role',
    key: 'role',
    title: '角色',
  },
  {
    dataIndex: 'communityName',
    key: 'communityName',
    title: '所属社区',
  },
  {
    dataIndex: 'riskLevel',
    key: 'riskLevel',
    title: '风险状态',
  },
  {
    dataIndex: 'bindCount',
    key: 'bindCount',
    title: '绑定关系',
  },
  {
    dataIndex: 'lastAlertAt',
    key: 'lastAlertAt',
    title: '最近告警',
  },
  {
    dataIndex: 'status',
    key: 'status',
    title: '账号状态',
  },
];

function getRoleLabel(role: AdminUserListItem['role']) {
  return roleTextMap[role];
}

function getRiskColor(level: AdminUserListItem['riskLevel']) {
  return riskColorMap[level];
}

function getRiskLabel(level: AdminUserListItem['riskLevel']) {
  return riskTextMap[level];
}

function getStatusColor(status: AdminUserListItem['status']) {
  return statusColorMap[status];
}

function getStatusLabel(status: AdminUserListItem['status']) {
  return statusTextMap[status];
}

async function loadUsers() {
  loading.value = true;
  try {
    const data = await getAdminUserListApi({
      keyword: filters.keyword || undefined,
      page: filters.page,
      pageSize: filters.pageSize,
      role: filters.role,
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
  void loadUsers();
}

function handleReset() {
  filters.keyword = '';
  filters.page = 1;
  filters.pageSize = 5;
  filters.role = undefined;
  filters.status = undefined;
  void loadUsers();
}

function handleTableChange(page: number, pageSize: number) {
  filters.page = page;
  filters.pageSize = pageSize;
  void loadUsers();
}

onMounted(() => {
  void loadUsers();
});
</script>

<template>
  <div class="admin-users-page">
    <section class="hero-panel">
      <div>
        <p class="eyebrow">管理后台 / 第一阶段</p>
        <h1>用户管理</h1>
        <p class="description">
          当前页面用于承接比赛演示中的账号、角色和权限管理，可按角色、状态和关键词筛选用户，快速定位重点对象和异常账号。
        </p>
      </div>
      <div class="hero-tip">
        <span>重点用于展示“系统可配置、角色可区分、风险对象可追踪”的后台能力。</span>
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
      <Space :size="12" wrap>
        <Input
          v-model:value="filters.keyword"
          allow-clear
          placeholder="搜索姓名、手机号、社区或编号"
          style="width: 260px"
          @press-enter="handleSearch"
        />
        <Select
          v-model:value="filters.role"
          allow-clear
          placeholder="角色"
          style="width: 180px"
          :options="[
            { label: '老年用户', value: 'elder' },
            { label: '子女用户', value: 'family' },
            { label: '社区工作人员', value: 'community' },
            { label: '管理员', value: 'admin' },
          ]"
        />
        <Select
          v-model:value="filters.status"
          allow-clear
          placeholder="状态"
          style="width: 140px"
          :options="[
            { label: '启用', value: 'enabled' },
            { label: '停用', value: 'disabled' },
          ]"
        />
        <Button type="primary" @click="handleSearch">查询</Button>
        <Button @click="handleReset">重置</Button>
      </Space>
    </Card>

    <Card class="table-card" :bordered="false">
      <Table
        :columns="columns"
        :data-source="rows"
        :loading="loading"
        :pagination="{
          current: filters.page,
          pageSize: filters.pageSize,
          showSizeChanger: true,
          total,
          onChange: handleTableChange,
          onShowSizeChange: handleTableChange,
        }"
        row-key="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'name'">
            <div class="user-cell">
              <strong>{{ record.name }}</strong>
              <span>{{ record.id }} · {{ record.phone }}</span>
              <span>{{ record.age }} 岁 · {{ record.createdAt }} 注册</span>
            </div>
          </template>

          <template v-else-if="column.key === 'role'">
            <Tag color="blue">{{ getRoleLabel(record.role) }}</Tag>
          </template>

          <template v-else-if="column.key === 'riskLevel'">
            <div class="risk-cell">
              <Tag :color="getRiskColor(record.riskLevel)">
                {{ getRiskLabel(record.riskLevel) }}
              </Tag>
              <span>风险分 {{ record.riskScore }}</span>
            </div>
          </template>

          <template v-else-if="column.key === 'bindCount'">
            <span>{{ record.bindCount }} 个关联对象</span>
          </template>

          <template v-else-if="column.key === 'status'">
            <Tag :color="getStatusColor(record.status)">
              {{ getStatusLabel(record.status) }}
            </Tag>
          </template>
        </template>

        <template #emptyText>
          <Empty description="当前筛选条件下暂无用户数据" />
        </template>
      </Table>
    </Card>
  </div>
</template>

<style scoped>
.admin-users-page {
  min-height: 100%;
  padding: 24px;
  background:
    radial-gradient(circle at top right, rgb(37 99 235 / 12%), transparent 28%),
    linear-gradient(180deg, #f8fbff 0%, #eef4ff 100%);
}

.hero-panel,
.filter-card,
.table-card,
.summary-card {
  background: rgb(255 255 255 / 94%);
  border: 1px solid rgb(59 130 246 / 12%);
  border-radius: 24px;
  box-shadow: 0 16px 40px rgb(15 23 42 / 6%);
}

.hero-panel {
  display: flex;
  gap: 24px;
  justify-content: space-between;
  padding: 28px 30px;
}

.eyebrow {
  margin: 0 0 12px;
  font-size: 13px;
  font-weight: 700;
  color: #2563eb;
  letter-spacing: 0.08em;
}

h1 {
  margin: 0;
  font-size: 32px;
  color: #0f172a;
}

.description {
  max-width: 720px;
  margin: 16px 0 0;
  font-size: 15px;
  line-height: 1.8;
  color: #475569;
}

.hero-tip {
  display: flex;
  align-items: flex-start;
  max-width: 320px;
  padding: 16px 18px;
  line-height: 1.7;
  color: #1e3a8a;
  background: rgb(37 99 235 / 8%);
  border-radius: 18px;
}

.summary-row {
  margin-top: 18px;
}

.summary-title,
.summary-desc {
  margin: 0;
}

.summary-title {
  font-size: 14px;
  color: #64748b;
}

.summary-value {
  display: block;
  margin-top: 10px;
  font-size: 30px;
  color: #0f172a;
}

.summary-desc {
  margin-top: 12px;
  line-height: 1.7;
  color: #475569;
}

.filter-card,
.table-card {
  margin-top: 18px;
}

.user-cell,
.risk-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.user-cell strong {
  color: #0f172a;
}

.user-cell span,
.risk-cell span {
  font-size: 13px;
  color: #64748b;
}

@media (max-width: 768px) {
  .admin-users-page {
    padding: 16px;
  }

  .hero-panel {
    flex-direction: column;
    padding: 22px;
  }

  h1 {
    font-size: 28px;
  }

  .hero-tip {
    max-width: none;
  }
}
</style>
