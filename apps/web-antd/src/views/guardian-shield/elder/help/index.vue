<script lang="ts" setup>
import { computed, ref } from 'vue';

import { Button, Card, Col, Divider, List, Modal, Row, Tag } from 'ant-design-vue';

defineOptions({ name: 'ElderHelp' });

interface HelpContact {
  id: string;
  name: string;
  note: string;
  phone: string;
  relation: string;
  responseTime: string;
  type: 'community' | 'family';
}

const contacts: HelpContact[] = [
  {
    id: 'HC-1',
    name: '李静',
    note: '默认第一联系人，遇到高风险会优先通知。',
    phone: '138****1024',
    relation: '女儿',
    responseTime: '预计 5 分钟内回电',
    type: 'family',
  },
  {
    id: 'HC-2',
    name: '王磊',
    note: '备用联系人，负责晚间协助核实。',
    phone: '139****5518',
    relation: '儿子',
    responseTime: '预计 10 分钟内回电',
    type: 'family',
  },
  {
    id: 'HC-3',
    name: '东湖社区值班台',
    note: '高风险场景可同步社区工作人员。',
    phone: '027-8***-2211',
    relation: '社区',
    responseTime: '工作时段 15 分钟内响应',
    type: 'community',
  },
];

const helpActions = [
  {
    description: '适合刚看到可疑电话、短信，需要立刻有人帮您判断。',
    title: '联系家人',
  },
  {
    description: '适合已经被持续催促、担心自己处理不了的时候。',
    title: '同步社区',
  },
  {
    description: '会保留时间、联系人和说明，方便后续回访。',
    title: '记录求助',
  },
];

const selectedAction = ref<string>('');
const actionVisible = ref(false);

const familyContacts = computed(() =>
  contacts.filter((item) => item.type === 'family'),
);
const communityContact = computed(() =>
  contacts.find((item) => item.type === 'community'),
);

function openAction(title: string) {
  selectedAction.value = title;
  actionVisible.value = true;
}
</script>

<template>
  <div class="elder-help-page">
    <section class="hero-panel">
      <div>
        <p class="eyebrow">老年端 / 快速求助</p>
        <h1>一键求助</h1>
        <p class="description">
          当您拿不准是不是诈骗时，不用自己硬判断。按下面的大按钮，就能优先联系家人，并在需要时同步社区。
        </p>
      </div>
      <div class="hero-note">
        <strong>先做这 3 件事</strong>
        <span>先挂电话，不转账，不说验证码。</span>
      </div>
    </section>

    <Row :gutter="[16, 16]" class="action-row">
      <Col v-for="item in helpActions" :key="item.title" :lg="8" :span="24">
        <Card class="action-card" :bordered="false">
          <h3>{{ item.title }}</h3>
          <p>{{ item.description }}</p>
          <Button block size="large" type="primary" @click="openAction(item.title)">
            立即操作
          </Button>
        </Card>
      </Col>
    </Row>

    <Row :gutter="[16, 16]" class="content-row">
      <Col :lg="15" :span="24">
        <Card class="list-card" :bordered="false" title="家人联系人">
          <List :data-source="familyContacts">
            <template #renderItem="{ item }">
              <List.Item class="contact-item">
                <div class="contact-main">
                  <div>
                    <div class="contact-head">
                      <h3>{{ item.name }}</h3>
                      <Tag color="gold">{{ item.relation }}</Tag>
                    </div>
                    <p class="contact-phone">{{ item.phone }}</p>
                    <p class="contact-note">{{ item.note }}</p>
                  </div>
                  <div class="contact-side">
                    <span>{{ item.responseTime }}</span>
                    <Button type="primary" @click="openAction(`联系${item.name}`)">联系</Button>
                  </div>
                </div>
              </List.Item>
            </template>
          </List>
        </Card>
      </Col>
      <Col :lg="9" :span="24">
        <Card class="tips-card" :bordered="false" title="社区支持">
          <div v-if="communityContact" class="community-contact">
            <h3>{{ communityContact.name }}</h3>
            <p>{{ communityContact.phone }}</p>
            <p>{{ communityContact.note }}</p>
            <Button block size="large" @click="openAction('同步社区值班台')">通知社区</Button>
          </div>
          <Divider />
          <div class="help-steps">
            <p class="steps-title">求助后会发生什么</p>
            <ul>
              <li>系统先通知默认家属联系人。</li>
              <li>高风险事件会提示同步社区。</li>
              <li>本次求助会留下时间和说明记录。</li>
            </ul>
          </div>
        </Card>
      </Col>
    </Row>

    <Modal v-model:open="actionVisible" title="求助动作已准备" ok-text="我知道了" cancel-text="关闭">
      <p>已为“{{ selectedAction }}”预留操作入口。</p>
      <p>当前版本先完成联系人展示与动作入口，后续可继续接入拨号、站内通知和处置留痕。</p>
    </Modal>
  </div>
</template>

<style scoped>
.elder-help-page {
  min-height: 100%;
  padding: 24px;
  background:
    radial-gradient(circle at top right, rgba(220, 38, 38, 0.12), transparent 28%),
    linear-gradient(180deg, #fff9f5 0%, #fff2ea 100%);
}

.hero-panel,
.action-card,
.list-card,
.tips-card {
  border: 1px solid rgba(249, 115, 22, 0.14);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 16px 36px rgba(124, 45, 18, 0.08);
}

.hero-panel {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  padding: 28px 30px;
}

.eyebrow {
  margin: 0 0 12px;
  color: #ea580c;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.08em;
}

h1 {
  margin: 0;
  color: #7c2d12;
  font-size: 34px;
}

.description {
  max-width: 760px;
  margin: 16px 0 0;
  color: #7c4a2d;
  font-size: 16px;
  line-height: 1.9;
}

.hero-note {
  max-width: 280px;
  padding: 18px;
  border-radius: 20px;
  background: #fff7ed;
  color: #9a3412;
  line-height: 1.9;
}

.action-row,
.content-row {
  margin-top: 18px;
}

.action-card {
  height: 100%;
}

.action-card h3,
.contact-head h3,
.community-contact h3 {
  margin: 0;
  color: #7c2d12;
}

.action-card p {
  min-height: 54px;
  color: #7c4a2d;
  line-height: 1.8;
}

.contact-item {
  padding: 8px 0;
}

.contact-main {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  width: 100%;
}

.contact-head {
  display: flex;
  align-items: center;
  gap: 8px;
}

.contact-phone,
.contact-note,
.community-contact p {
  margin: 8px 0 0;
  color: #7c4a2d;
  line-height: 1.8;
}

.contact-side {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 12px;
  min-width: 160px;
  color: #9a3412;
}

.steps-title {
  margin: 0 0 8px;
  color: #c2410c;
  font-weight: 700;
}

.help-steps ul {
  margin: 0;
  padding-left: 20px;
  color: #7c4a2d;
  line-height: 1.9;
}

@media (max-width: 768px) {
  .elder-help-page {
    padding: 16px;
  }

  .hero-panel,
  .contact-main {
    flex-direction: column;
  }

  h1 {
    font-size: 28px;
  }

  .contact-side {
    min-width: 0;
  }
}
</style>
