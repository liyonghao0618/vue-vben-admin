<script lang="ts" setup>
import { computed, onMounted, ref } from 'vue';

import { Card, Col, Row, Space, Tag } from 'ant-design-vue';

import { getRolePermissionOverviewApi } from '#/api';
import type { RolePermissionOverviewItem } from '#/api';

defineOptions({ name: 'AdminRoles' });

const loading = ref(false);
const rows = ref<RolePermissionOverviewItem[]>([]);

const summaryCards = computed(() => [
  {
    title: '角色数量',
    value: `${rows.value.length}`,
    description: '当前系统内可见的角色类型。',
  },
  {
    title: '菜单总数',
    value: `${rows.value.reduce((sum, item) => sum + item.menuCount, 0)}`,
    description: '用于快速查看不同角色可访问页面数量。',
  },
  {
    title: '权限项总数',
    value: `${rows.value.reduce((sum, item) => sum + item.codeCount, 0)}`,
    description: '为后续精细化权限控制提供口径。',
  },
]);

async function loadRows() {
  loading.value = true;
  try {
    rows.value = await getRolePermissionOverviewApi();
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  void loadRows();
});
</script>

<template>
  <div class="admin-roles-page">
    <section class="hero-panel">
      <div>
        <p class="eyebrow">管理后台 / 权限总览</p>
        <h1>角色权限</h1>
        <p class="description">
          当前页面已经接入角色权限 mock 数据，支持查看角色说明、菜单项和权限资源，满足第一阶段“角色查看与权限项展示”目标。
        </p>
      </div>
    </section>

    <Row :gutter="[16, 16]" class="summary-row">
      <Col v-for="item in summaryCards" :key="item.title" :lg="8" :span="24">
        <Card class="summary-card" :bordered="false">
          <p class="summary-title">{{ item.title }}</p>
          <strong class="summary-value">{{ item.value }}</strong>
          <p class="summary-desc">{{ item.description }}</p>
        </Card>
      </Col>
    </Row>

    <Row :gutter="[16, 16]" class="list-row">
      <Col v-for="item in rows" :key="item.role" :lg="12" :span="24">
        <Card class="role-card" :bordered="false" :loading="loading">
          <div class="role-head">
            <div>
              <h3>{{ item.name }}</h3>
              <p>{{ item.scope }}</p>
            </div>
            <Space>
              <Tag color="blue">{{ item.menuCount }} 个菜单</Tag>
              <Tag color="gold">{{ item.codeCount }} 个权限项</Tag>
            </Space>
          </div>
          <p class="role-desc">{{ item.description }}</p>
          <div class="block">
            <p class="label">可访问菜单</p>
            <Space wrap>
              <Tag v-for="menu in item.menus" :key="menu">{{ menu }}</Tag>
            </Space>
          </div>
          <div class="block">
            <p class="label">权限资源</p>
            <Space wrap>
              <Tag v-for="resource in item.resources" :key="resource" color="processing">
                {{ resource }}
              </Tag>
            </Space>
          </div>
        </Card>
      </Col>
    </Row>
  </div>
</template>

<style scoped>
.admin-roles-page {
  min-height: 100%;
  padding: 24px;
  background:
    radial-gradient(circle at top right, rgba(59, 130, 246, 0.12), transparent 28%),
    linear-gradient(180deg, #f8fbff 0%, #eef4ff 100%);
}

.hero-panel,
.summary-card,
.role-card {
  border: 1px solid rgba(59, 130, 246, 0.14);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 16px 36px rgba(30, 64, 175, 0.08);
}

.hero-panel {
  padding: 28px 30px;
}

.eyebrow {
  margin: 0 0 12px;
  color: #2563eb;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.08em;
}

h1 {
  margin: 0;
  color: #1d4ed8;
  font-size: 34px;
}

.description {
  margin: 16px 0 0;
  color: #334155;
  line-height: 1.8;
}

.summary-row,
.list-row {
  margin-top: 18px;
}

.summary-title,
.summary-desc {
  margin: 0;
}

.summary-title {
  color: #1d4ed8;
}

.summary-value {
  display: block;
  margin-top: 10px;
  color: #172554;
  font-size: 30px;
}

.summary-desc {
  margin-top: 12px;
  color: #475569;
  line-height: 1.7;
}

.role-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
}

.role-head h3 {
  margin: 0;
  color: #1e3a8a;
}

.role-head p,
.role-desc {
  margin: 8px 0 0;
  color: #475569;
  line-height: 1.8;
}

.block {
  margin-top: 16px;
}

.label {
  margin: 0 0 10px;
  color: #1d4ed8;
  font-weight: 700;
}

@media (max-width: 768px) {
  .admin-roles-page {
    padding: 16px;
  }

  .role-head {
    flex-direction: column;
  }

  h1 {
    font-size: 28px;
  }
}
</style>
