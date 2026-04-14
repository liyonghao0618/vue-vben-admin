import { eventHandler, getQuery } from 'h3';

import { verifyAccessToken } from '~/utils/jwt-utils';
import {
  sleep,
  unAuthorizedResponse,
  usePageResponseSuccess,
} from '~/utils/response';

interface FamilyAlertItem {
  advice: string;
  contactSuggestion: string;
  elderName: string;
  handledAt?: string;
  hitReason: string;
  id: string;
  occurredAt: string;
  readStatus: 'read' | 'unread';
  remoteMessage: string;
  riskLevel: 'high' | 'low' | 'medium';
  riskScore: number;
  sourceType: 'call' | 'sms';
  status: 'handled' | 'pending';
  title: string;
}

const MOCK_FAMILY_ALERTS: FamilyAlertItem[] = [
  {
    advice: '先联系老人确认，不要点击链接，不要输入银行卡信息。',
    contactSuggestion: '建议同步社区工作人员并提醒主联系人跟进。',
    elderName: '王阿姨',
    hitReason: '命中“医保账户异常”“立即验证”“点击链接”等高风险词。',
    id: 'FAM-3001',
    occurredAt: '2026-04-14 09:12',
    readStatus: 'unread',
    remoteMessage: '妈，先别点链接，也别输验证码，我马上给你打电话。',
    riskLevel: 'high',
    riskScore: 94,
    sourceType: 'sms',
    status: 'pending',
    title: '疑似冒充医保短信',
  },
  {
    advice: '先挂断电话，不要转账，不按对方提示操作。',
    contactSuggestion: '建议让老人先停止沟通，由家属回拨官方渠道核实。',
    elderName: '周奶奶',
    hitReason: '命中“公检法”“安全账户”“立即转账”等诈骗话术。',
    id: 'FAM-3002',
    occurredAt: '2026-04-14 08:45',
    readStatus: 'read',
    remoteMessage: '这是诈骗话术，先挂断电话，等我联系你。',
    riskLevel: 'high',
    riskScore: 91,
    sourceType: 'call',
    status: 'handled',
    title: '疑似冒充公检法来电',
    handledAt: '2026-04-14 08:58',
  },
  {
    advice: '验证码只给官方平台，不告诉陌生人。',
    contactSuggestion: '建议提示老人今后遇到退款问题先找子女确认。',
    elderName: '孙大爷',
    hitReason: '命中“退款”“验证码”“退费”等套取信息模式。',
    id: 'FAM-3003',
    occurredAt: '2026-04-13 18:20',
    readStatus: 'read',
    remoteMessage: '别把验证码告诉别人，退款我帮你核实。',
    riskLevel: 'medium',
    riskScore: 67,
    sourceType: 'sms',
    status: 'handled',
    title: '疑似退款验证码套取',
    handledAt: '2026-04-13 18:35',
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
  const status = normalizeQueryValue(query.status);
  const readStatus = normalizeQueryValue(query.readStatus);

  let listData = structuredClone(MOCK_FAMILY_ALERTS);

  if (riskLevel) {
    listData = listData.filter((item) => item.riskLevel === riskLevel);
  }
  if (status) {
    listData = listData.filter((item) => item.status === status);
  }
  if (readStatus) {
    listData = listData.filter((item) => item.readStatus === readStatus);
  }

  return usePageResponseSuccess(String(page), String(pageSize), listData);
});
