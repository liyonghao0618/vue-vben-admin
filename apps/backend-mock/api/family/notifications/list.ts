import { eventHandler, getQuery } from 'h3';

import { verifyAccessToken } from '~/utils/jwt-utils';
import {
  sleep,
  unAuthorizedResponse,
  usePageResponseSuccess,
} from '~/utils/response';

interface FamilyNotificationItem {
  channel: 'app' | 'sms' | 'voice';
  elderName: string;
  id: string;
  notifiedAt: string;
  operatorName: string;
  readStatus: 'read' | 'unread';
  relatedAlertTitle: string;
  result: 'delivered' | 'failed' | 'processing';
  riskLevel: 'high' | 'low' | 'medium';
  status: 'closed' | 'follow_up' | 'pending';
}

const MOCK_FAMILY_NOTIFICATIONS: FamilyNotificationItem[] = [
  {
    channel: 'app',
    elderName: '王阿姨',
    id: 'NTF-4001',
    notifiedAt: '2026-04-14 09:13',
    operatorName: '系统自动通知',
    readStatus: 'unread',
    relatedAlertTitle: '疑似冒充医保短信',
    result: 'delivered',
    riskLevel: 'high',
    status: 'pending',
  },
  {
    channel: 'voice',
    elderName: '周奶奶',
    id: 'NTF-4002',
    notifiedAt: '2026-04-14 08:47',
    operatorName: '社区值守专员',
    readStatus: 'read',
    relatedAlertTitle: '疑似冒充公检法来电',
    result: 'delivered',
    riskLevel: 'high',
    status: 'follow_up',
  },
  {
    channel: 'sms',
    elderName: '孙大爷',
    id: 'NTF-4003',
    notifiedAt: '2026-04-13 18:22',
    operatorName: '系统自动通知',
    readStatus: 'read',
    relatedAlertTitle: '疑似退款验证码套取',
    result: 'delivered',
    riskLevel: 'medium',
    status: 'closed',
  },
  {
    channel: 'app',
    elderName: '赵桂兰',
    id: 'NTF-4004',
    notifiedAt: '2026-04-12 16:39',
    operatorName: '系统自动通知',
    readStatus: 'read',
    relatedAlertTitle: '疑似熟人冒充来电',
    result: 'processing',
    riskLevel: 'low',
    status: 'pending',
  },
];

function normalizeQueryValue(value: string | string[] | undefined) {
  return Array.isArray(value) ? value[0] : value;
}

export default eventHandler(async (event) => {
  const userinfo = verifyAccessToken(event);
  if (!userinfo) {
    return unAuthorizedResponse(event);
  }

  await sleep(300);

  const query = getQuery(event);
  const page = Math.max(
    1,
    Number.parseInt(normalizeQueryValue(query.page) || '1', 10) || 1,
  );
  const pageSize = Math.min(
    20,
    Math.max(
      1,
      Number.parseInt(normalizeQueryValue(query.pageSize) || '5', 10) || 5,
    ),
  );
  const riskLevel = normalizeQueryValue(query.riskLevel);
  const readStatus = normalizeQueryValue(query.readStatus);
  const status = normalizeQueryValue(query.status);

  let listData = structuredClone(MOCK_FAMILY_NOTIFICATIONS);

  if (riskLevel) {
    listData = listData.filter((item) => item.riskLevel === riskLevel);
  }
  if (readStatus) {
    listData = listData.filter((item) => item.readStatus === readStatus);
  }
  if (status) {
    listData = listData.filter((item) => item.status === status);
  }

  return usePageResponseSuccess(String(page), String(pageSize), listData);
});
