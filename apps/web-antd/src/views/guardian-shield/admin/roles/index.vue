<script lang="ts" setup>
import { computed, onMounted, ref } from 'vue';

import { Card, Col, List, Row, Space, Tag } from 'ant-design-vue';

import { getRolePermissionOverviewApi } from '#/api';
import type { RolePermissionOverviewItem } from '#/api';

defineOptions({ name: 'AdminRoles' });

const loading = ref(false);
const roles = ref<RolePermissionOverviewItem[]>([]);

const summaryCards = computed(() => [
  {
    title: '基础角色',
    value: `${roles.value.length}`,
    description: '当前已接入 elder、family、community、admin 四类基础角色。',
  },
  {
    title: '菜单总量',
    value: `${roles.value.reduce((sum, item) => sum + item.menuCount, 0)}`,
    description: '展示各角色当前可访问的菜单规模。',
  },
  {
    title: '权限码总量',
    value: `${roles.value.reduce((sum, item) => sum + item.codeCount, 0)}`,
    description: '为后续按钮权限和接口权限扩展预留口径。',
  },
  {
    title: '权限骨架',
    value: '已联通',
    description: '已实现角色登录、菜单返回与权限码展示链路。',
  },
]);

async function loadRoles() {
  loading.value = true;
  try {
    roles.value = await getRolePermissionOverviewApi();
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  void loadRoles();
});
</script>

<template>
  <div class="admin-roles-page">
    <section class="hero-panel">
      <div>
        <p class="eyebrow">管理后台 / 权限骨架</p>
        <h1>角色权限</h1>
        <p class="description">
          当前页面已经接入真实 mock 角色权限概览，可查看各角色菜单、权限码和业务职责，作为第一阶段权限体系的可视化入口。
        </p>
      </div>
    </section>

    <Row :gutter="[16, 16]" class="summary-row">
      <Col v-for="item in summaryCards" :key="item.title" :lg="6" :md="12" :span="24">
        <Card class="summary-card" :bordered="false">
          <p class="summary-title">{{ item.title }}</p>
          <strong class="summary-value">{{ item.value }}</strong>
          <p class="summary-desc">{{ item.description }}</p>
        </Card>
      </Col>
    </Row>

    <Card class="list-card" :bordered="false">
      <List
        :data-source="roles"
        :loading="loading"
        :locale="{ emptyText: '暂无角色权限数据' }"
        item-layout="vertical"
      >
        <template #renderItem="{ item }">
          <List.Item class="role-item">
            <div class="role-header">
              <div>
                <h3>{{ item.name }}</h3>
                <p class="role-meta">{{ item.role }} · {{ item.scope }}</p>
              </div>
              <Space wrap>
                <Tag color="blue">{{ item.menuCount }} 个菜单</Tag>
                <Tag color="purple">{{ item.codeCount }} 个权限码</Tag>
              </Space>
            </div>
            <p class="description-text">{{ item.description }}</p>

            <Row :gutter="[16, 16]">
              <Col :lg="12" :span="24">
                <div class="info-card">
                  <p class="info-label">菜单范围</p>
                  <Space wrap>
                    <Tag v-for="menu in item.menus" :key="menu" color="blue">
                      {{ menu }}
                    </Tag>
                  </Space>
                </div>
              </Col>
              <Col :lg="12" :span="24">
                <div class="info-card">
                  <p class="info-label">权限码</p>
                  <Space wrap>
                    <Tag v-for="resource in item.resources" :key="resource" color="purple">
                      {{ resource }}
                    </Tag>
                  </Space>
                </div>
              </Col>
            </Row>
          </List.Item>
        </template>
      </List>
    </Card>
  </div>
</template>

<style scoped>
.admin-roles-page {
  min-height: 100%;
  padding: 24px;
  background:
    radial-gradient(circle at top right, rgba(124, 58, 237, 0.12), transparent 28%),
    linear-gradient(180deg, #faf8ff 0%, #f3f0ff 100%);
}

.hero-panel,
.summary-card,
.list-card,
.info-card {
  border: 1px solid rgba(124, 58, 237, 0.12);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 16px 36px rgba(91, 33, 182, 0.08);
}

.hero-panel {
  padding: 28px 30px;
}

.eyebrow {
  margin: 0 0 12px;
  color: #7c3aed;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.08em;
}

h1, h3 {
  margin: 0;
  color: #4c1d95;
}

.description,
.summary-desc,
.description-text,
.role-meta {
  color: #6d28d9;
}

.description {
  max-width: 760px;
  margin-top: 16px;
  line-height: 1.8;
}

.summary-row,
.list-card {
  margin-top: 18px;
}

.summary-title {
  margin: 0;
  color: #7c3aed;
}

.summary-value {
  display: block;
  margin-top: 10px;
  color: #4c1d95;
  font-size: 30px;
}

.summary-desc,
.description-text,
.role-meta {
  margin-top: 10px;
  line-height: 1.7;
}

.role-item {
  padding: 6px 0 20px;
}

.role-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
}

.info-card {
  height: 100%;
  padding: 18px;
}

.info-label {
  margin: 0 0 12px;
  color: #7c3aed;
  font-weight: 700;
}

@media (max-width: 768px) {
  .admin-roles-page,
  .family-alerts-page,
  .family-notifications-page {
    padding: 16px;
  }

  .role-header {
    flex-direction: column;
  }
}
</style>
