import { eventHandler } from 'h3';

import { verifyAccessToken } from '~/utils/jwt-utils';
import { sleep, unAuthorizedResponse, useResponseSuccess } from '~/utils/response';

const ROLE_PERMISSION_OVERVIEW = [
  {
    codeCount: 3,
    description: '面向老年用户，强调适老化提醒、一键求助与亲属绑定。',
    menuCount: 6,
    menus: ['首页', '风险提醒', '一键求助', '亲属绑定', '防骗知识', '适老设置'],
    name: '老年用户',
    resources: ['risk:view', 'alert:help', 'family:bind'],
    role: 'elder',
    scope: '查看个人风险提醒与求助入口',
  },
  {
    codeCount: 3,
    description: '面向子女用户，提供风险通知、远程提醒和处置反馈。',
    menuCount: 5,
    menus: ['监护总览', '老人列表', '风险详情', '通知记录', '监护设置'],
    name: '子女用户',
    resources: ['family:overview', 'family:notify', 'family:feedback'],
    role: 'family',
    scope: '查看被监护老人并接收高风险通知',
  },
  {
    codeCount: 3,
    description: '面向社区工作人员，负责辖区总览、重点老人和工单处置。',
    menuCount: 5,
    menus: ['辖区总览', '重点老人', '风险工单', '宣教管理', '统计报表'],
    name: '社区工作人员',
    resources: ['community:dashboard', 'community:workorder', 'community:report'],
    role: 'community',
    scope: '管理辖区风险事件与宣教工作',
  },
  {
    codeCount: 4,
    description: '面向系统管理员，负责用户、角色、规则与内容配置。',
    menuCount: 5,
    menus: ['用户管理', '角色权限', '风险规则', '内容管理', '系统配置'],
    name: '系统管理员',
    resources: ['system:user', 'system:role', 'system:rule', 'system:content'],
    role: 'admin',
    scope: '拥有平台配置与权限管理能力',
  },
];

export default eventHandler(async (event) => {
  const userinfo = verifyAccessToken(event);
  if (!userinfo) {
    return unAuthorizedResponse(event);
  }

  await sleep(250);

  return useResponseSuccess(ROLE_PERMISSION_OVERVIEW);
});
