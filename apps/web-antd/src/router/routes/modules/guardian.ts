import type { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    meta: {
      icon: 'lucide:heart-handshake',
      title: '老年端',
      authority: ['elder'],
    },
    name: 'ElderPortal',
    path: '/elder',
    redirect: '/elder/home',
    children: [
      {
        name: 'ElderHome',
        path: '/elder/home',
        component: () => import('#/views/guardian-shield/elder/home/index.vue'),
        meta: {
          affixTab: true,
          authority: ['elder'],
          icon: 'lucide:house',
          title: '首页',
        },
      },
      {
        name: 'ElderAlerts',
        path: '/elder/alerts',
        component: () =>
          import('#/views/guardian-shield/elder/alerts/index.vue'),
        meta: {
          authority: ['elder'],
          icon: 'lucide:shield-alert',
          title: '风险提醒',
        },
      },
      {
        name: 'ElderHelp',
        path: '/elder/help',
        component: () => import('#/views/guardian-shield/elder/help/index.vue'),
        meta: {
          authority: ['elder'],
          icon: 'lucide:siren',
          title: '一键求助',
        },
      },
      {
        name: 'ElderFamilyBinding',
        path: '/elder/family-binding',
        component: () =>
          import('#/views/guardian-shield/elder/family-binding/index.vue'),
        meta: {
          authority: ['elder'],
          icon: 'lucide:users',
          title: '亲属绑定',
        },
      },
      {
        name: 'ElderKnowledge',
        path: '/elder/knowledge',
        component: () =>
          import('#/views/guardian-shield/elder/knowledge/index.vue'),
        meta: {
          authority: ['elder'],
          icon: 'lucide:book-open',
          title: '防骗知识',
        },
      },
      {
        name: 'ElderSettings',
        path: '/elder/settings',
        component: () =>
          import('#/views/guardian-shield/elder/settings/index.vue'),
        meta: {
          authority: ['elder'],
          icon: 'lucide:settings',
          title: '适老设置',
        },
      },
    ],
  },
  {
    meta: {
      icon: 'lucide:bell-ring',
      title: '子女端',
      authority: ['family'],
    },
    name: 'FamilyPortal',
    path: '/family',
    redirect: '/family/overview',
    children: [
      {
        name: 'FamilyOverview',
        path: '/family/overview',
        component: () =>
          import('#/views/guardian-shield/family/overview/index.vue'),
        meta: {
          affixTab: true,
          authority: ['family'],
          icon: 'lucide:layout-dashboard',
          title: '监护总览',
        },
      },
      {
        name: 'FamilySeniors',
        path: '/family/seniors',
        component: () =>
          import('#/views/guardian-shield/family/seniors/index.vue'),
        meta: {
          authority: ['family'],
          icon: 'lucide:users-round',
          title: '老人列表',
        },
      },
      {
        name: 'FamilyAlerts',
        path: '/family/alerts',
        component: () =>
          import('#/views/guardian-shield/family/alerts/index.vue'),
        meta: {
          authority: ['family'],
          icon: 'lucide:shield-alert',
          title: '风险详情',
        },
      },
      {
        name: 'FamilyNotifications',
        path: '/family/notifications',
        component: () =>
          import('#/views/guardian-shield/family/notifications/index.vue'),
        meta: {
          authority: ['family'],
          icon: 'lucide:mail-warning',
          title: '通知记录',
        },
      },
      {
        name: 'FamilySettings',
        path: '/family/settings',
        component: () =>
          import('#/views/guardian-shield/family/settings/index.vue'),
        meta: {
          authority: ['family'],
          icon: 'lucide:sliders-horizontal',
          title: '监护设置',
        },
      },
    ],
  },
  {
    meta: {
      icon: 'lucide:building-2',
      title: '社区端',
      authority: ['community'],
    },
    name: 'CommunityPortal',
    path: '/community',
    redirect: '/community/dashboard',
    children: [
      {
        name: 'CommunityDashboard',
        path: '/community/dashboard',
        component: () =>
          import('#/views/guardian-shield/community/dashboard/index.vue'),
        meta: {
          affixTab: true,
          authority: ['community'],
          icon: 'lucide:chart-column-big',
          title: '辖区总览',
        },
      },
      {
        name: 'CommunitySeniors',
        path: '/community/seniors',
        component: () =>
          import('#/views/guardian-shield/community/seniors/index.vue'),
        meta: {
          authority: ['community'],
          icon: 'lucide:user-round-search',
          title: '重点老人',
        },
      },
      {
        name: 'CommunityWorkorders',
        path: '/community/workorders',
        component: () =>
          import('#/views/guardian-shield/community/workorders/index.vue'),
        meta: {
          authority: ['community'],
          icon: 'lucide:files',
          title: '风险工单',
        },
      },
      {
        name: 'CommunityEducation',
        path: '/community/education',
        component: () =>
          import('#/views/guardian-shield/community/education/index.vue'),
        meta: {
          authority: ['community'],
          icon: 'lucide:megaphone',
          title: '宣教管理',
        },
      },
      {
        name: 'CommunityReports',
        path: '/community/reports',
        component: () =>
          import('#/views/guardian-shield/community/reports/index.vue'),
        meta: {
          authority: ['community'],
          icon: 'lucide:file-bar-chart',
          title: '统计报表',
        },
      },
    ],
  },
  {
    meta: {
      icon: 'lucide:shield-check',
      title: '管理后台',
      authority: ['admin'],
    },
    name: 'AdminPortal',
    path: '/admin',
    redirect: '/admin/users',
    children: [
      {
        name: 'AdminUsers',
        path: '/admin/users',
        component: () =>
          import('#/views/guardian-shield/admin/users/index.vue'),
        meta: {
          affixTab: true,
          authority: ['admin'],
          icon: 'lucide:users',
          title: '用户管理',
        },
      },
      {
        name: 'AdminRoles',
        path: '/admin/roles',
        component: () =>
          import('#/views/guardian-shield/admin/roles/index.vue'),
        meta: {
          authority: ['admin'],
          icon: 'lucide:key-round',
          title: '角色权限',
        },
      },
      {
        name: 'AdminRules',
        path: '/admin/rules',
        component: () =>
          import('#/views/guardian-shield/admin/rules/index.vue'),
        meta: {
          authority: ['admin'],
          icon: 'lucide:scan-search',
          title: '风险规则',
        },
      },
      {
        name: 'AdminContents',
        path: '/admin/contents',
        component: () =>
          import('#/views/guardian-shield/admin/contents/index.vue'),
        meta: {
          authority: ['admin'],
          icon: 'lucide:book-copy',
          title: '内容管理',
        },
      },
      {
        name: 'AdminSystemSettings',
        path: '/admin/system-settings',
        component: () =>
          import('#/views/guardian-shield/admin/system-settings/index.vue'),
        meta: {
          authority: ['admin'],
          icon: 'lucide:settings-2',
          title: '系统配置',
        },
      },
    ],
  },
];

export default routes;
