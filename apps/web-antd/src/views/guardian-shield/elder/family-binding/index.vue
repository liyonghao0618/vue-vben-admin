<script lang="ts" setup>
import { computed, ref } from 'vue';

import { Button, Card, Col, List, Modal, Row, Space, Steps, Tag } from 'ant-design-vue';

defineOptions({ name: 'ElderFamilyBinding' });

interface FamilyBindingItem {
  id: string;
  isPrimary: boolean;
  lastAuthorizedAt: string;
  name: string;
  note: string;
  phone: string;
  relation: string;
  status: 'active' | 'expired';
}

const bindings = ref<FamilyBindingItem[]>([
  {
    id: 'FB-1',
    isPrimary: true,
    lastAuthorizedAt: '2026-04-12 10:20',
    name: '李静',
    note: '接收高风险通知和一键求助信息。',
    phone: '138****1024',
    relation: '女儿',
    status: 'active',
  },
  {
    id: 'FB-2',
    isPrimary: false,
    lastAuthorizedAt: '2026-03-28 18:10',
    name: '王磊',
    note: '作为备用联系人，夜间优先提醒。',
    phone: '139****5518',
    relation: '儿子',
    status: 'active',
  },
  {
    id: 'FB-3',
    isPrimary: false,
    lastAuthorizedAt: '2026-02-16 09:00',
    name: '周敏',
    note: '授权已到期，需重新确认后恢复通知。',
    phone: '137****2206',
    relation: '外甥女',
    status: 'expired',
  },
]);

const modalVisible = ref(false);
const modalTitle = ref('');

const availableSlots = computed(() => Math.max(0, 3 - bindings.value.length));

function openAction(title: string) {
  modalTitle.value = title;
  modalVisible.value = true;
}

function getStatusMeta(status: FamilyBindingItem['status']) {
  return status === 'active'
    ? { color: 'success', text: '已授权' }
    : { color: 'warning', text: '待重新授权' };
}
</script>

<template>
  <div class="elder-family-binding-page">
    <section class="hero-panel">
      <div>
        <p class="eyebrow">老年端 / 亲属绑定</p>
        <h1>亲属绑定</h1>
        <p class="description">
          您最多可以绑定 3 位家人。绑定后，系统可以在高风险场景提醒家人帮助您核实情况。
        </p>
      </div>
      <div class="hero-note">
        <strong>当前状态</strong>
        <span>已绑定 {{ bindings.length }} 人，还可新增 {{ availableSlots }} 人。</span>
      </div>
    </section>

    <Row :gutter="[16, 16]" class="content-row">
      <Col :lg="16" :span="24">
        <Card class="list-card" :bordered="false" title="已绑定亲属">
          <List :data-source="bindings">
            <template #renderItem="{ item }">
              <List.Item class="binding-item">
                <div class="binding-main">
                  <div>
                    <div class="binding-head">
                      <h3>{{ item.name }}</h3>
                      <Tag color="gold">{{ item.relation }}</Tag>
                      <Tag v-if="item.isPrimary" color="blue">默认联系人</Tag>
                      <Tag :color="getStatusMeta(item.status).color">
                        {{ getStatusMeta(item.status).text }}
                      </Tag>
                    </div>
                    <p class="binding-phone">{{ item.phone }}</p>
                    <p class="binding-note">{{ item.note }}</p>
                    <p class="binding-time">最近授权：{{ item.lastAuthorizedAt }}</p>
                  </div>
                  <Space wrap>
                    <Button @click="openAction(`重新授权 ${item.name}`)">重新授权</Button>
                    <Button danger @click="openAction(`解绑 ${item.name}`)">解绑</Button>
                  </Space>
                </div>
              </List.Item>
            </template>
          </List>
        </Card>
      </Col>
      <Col :lg="8" :span="24">
        <Card class="flow-card" :bordered="false" title="绑定流程">
          <Steps
            direction="vertical"
            :items="[
              { title: '新增家人', description: '填写姓名、手机号和关系。' },
              { title: '确认授权', description: '确认允许接收风险提醒和求助通知。' },
              { title: '后续管理', description: '支持解绑和重新授权。' },
            ]"
          />
          <div class="flow-actions">
            <Button block size="large" type="primary" @click="openAction('新增亲属绑定')">
              新增绑定
            </Button>
          </div>
        </Card>
      </Col>
    </Row>

    <Modal v-model:open="modalVisible" :title="modalTitle" ok-text="我知道了" cancel-text="关闭">
      <p>当前版本已完成绑定、解绑和重新授权的流程入口展示。</p>
      <p>下一步可继续接入表单提交、短信确认和真实绑定关系接口。</p>
    </Modal>
  </div>
</template>

<style scoped>
.elder-family-binding-page {
  min-height: 100%;
  padding: 24px;
  background:
    radial-gradient(circle at top right, rgba(14, 165, 233, 0.12), transparent 28%),
    linear-gradient(180deg, #f8fcff 0%, #eef7ff 100%);
}

.hero-panel,
.list-card,
.flow-card {
  border: 1px solid rgba(14, 165, 233, 0.14);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 16px 36px rgba(14, 116, 144, 0.08);
}

.hero-panel {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  padding: 28px 30px;
}

.eyebrow {
  margin: 0 0 12px;
  color: #0284c7;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.08em;
}

h1 {
  margin: 0;
  color: #0f172a;
  font-size: 34px;
}

.description {
  margin: 16px 0 0;
  max-width: 760px;
  color: #334155;
  font-size: 16px;
  line-height: 1.8;
}

.hero-note {
  max-width: 280px;
  padding: 18px;
  border-radius: 20px;
  background: #eff6ff;
  color: #075985;
  line-height: 1.8;
}

.content-row {
  margin-top: 18px;
}

.binding-item {
  padding: 10px 0;
}

.binding-main {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  width: 100%;
}

.binding-head {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.binding-head h3 {
  margin: 0;
  color: #0f172a;
}

.binding-phone,
.binding-note,
.binding-time {
  margin: 8px 0 0;
  color: #475569;
  line-height: 1.8;
}

.flow-actions {
  margin-top: 20px;
}

@media (max-width: 768px) {
  .elder-family-binding-page {
    padding: 16px;
  }

  .hero-panel,
  .binding-main {
    flex-direction: column;
  }

  h1 {
    font-size: 28px;
  }
}
</style>
