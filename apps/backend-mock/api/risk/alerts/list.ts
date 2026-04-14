import { eventHandler, getQuery } from 'h3';

import { verifyAccessToken } from '~/utils/jwt-utils';
import {
  sleep,
  unAuthorizedResponse,
  usePageResponseSuccess,
} from '~/utils/response';

interface RiskAlertItem {
  advice: string;
  contactSuggestion: string;
  contentPreview: string;
  hitReason: string;
  id: string;
  occurredAt: string;
  riskLevel: 'high' | 'low' | 'medium';
  riskScore: number;
  sourceType: 'call' | 'sms';
  status: 'handled' | 'pending';
  title: string;
}

const MOCK_RISK_ALERTS: RiskAlertItem[] = [
  {
    advice: '不要点击链接，不要输入银行卡和验证码，先联系子女核实。',
    contactSuggestion: '建议立即通知女儿并同步社区联系人。',
    contentPreview: '【紧急通知】您的医保账户异常，请立即点击链接完成验证。',
    hitReason: '命中“医保账户异常”“点击链接”“完成验证”等高风险诱导词。',
    id: 'ALT-2001',
    occurredAt: '2026-04-14 09:12',
    riskLevel: 'high',
    riskScore: 94,
    sourceType: 'sms',
    status: 'pending',
    title: '疑似冒充医保短信',
  },
  {
    advice: '先挂断电话，不要透露验证码，不要按对方提示操作。',
    contactSuggestion: '建议回拨官方客服电话核实，并通知家属。',
    contentPreview: '来电中反复强调“公检法调查”“安全账户”“立即转账”。',
    hitReason: '命中“公检法”“安全账户”“立即转账”等典型诈骗话术。',
    id: 'ALT-2002',
    occurredAt: '2026-04-14 08:45',
    riskLevel: 'high',
    riskScore: 91,
    sourceType: 'call',
    status: 'pending',
    title: '疑似冒充公检法来电',
  },
  {
    advice: '不要向陌生人提供验证码，涉及退款请通过官方平台处理。',
    contactSuggestion: '建议联系平台官方客服确认，不直接回复短信。',
    contentPreview: '对方称商品退款，需要提供验证码完成退费。',
    hitReason: '命中“退款”“验证码”“完成退费”等验证码套取模式。',
    id: 'ALT-2003',
    occurredAt: '2026-04-13 18:20',
    riskLevel: 'medium',
    riskScore: 67,
    sourceType: 'sms',
    status: 'handled',
    title: '疑似退款验证码套取',
  },
  {
    advice: '陌生中奖信息通常为骗局，不转账、不领奖、不点链接。',
    contactSuggestion: '建议标记为骚扰信息并告知子女关注。',
    contentPreview: '恭喜您获得现金大奖，请缴纳手续费后立即领取。',
    hitReason: '命中“现金大奖”“手续费”“立即领取”等中奖返利模式。',
    id: 'ALT-2004',
    occurredAt: '2026-04-13 12:02',
    riskLevel: 'medium',
    riskScore: 61,
    sourceType: 'sms',
    status: 'handled',
    title: '疑似中奖返利短信',
  },
  {
    advice: '陌生电话让您加好友或转到其他平台时，不要继续沟通。',
    contactSuggestion: '建议拉黑号码并在家属协助下核实身份。',
    contentPreview: '通话中对方自称熟人朋友，要求转到私聊软件继续联系。',
    hitReason: '命中“熟人冒充”“转移沟通渠道”等可疑模式。',
    id: 'ALT-2005',
    occurredAt: '2026-04-12 16:36',
    riskLevel: 'low',
    riskScore: 38,
    sourceType: 'call',
    status: 'handled',
    title: '疑似熟人冒充来电',
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
  const sourceType = normalizeQueryValue(query.sourceType);
  const riskLevel = normalizeQueryValue(query.riskLevel);
  const status = normalizeQueryValue(query.status);

  let listData = structuredClone(MOCK_RISK_ALERTS);

  if (sourceType) {
    listData = listData.filter((item) => item.sourceType === sourceType);
  }
  if (riskLevel) {
    listData = listData.filter((item) => item.riskLevel === riskLevel);
  }
  if (status) {
    listData = listData.filter((item) => item.status === status);
  }

  return usePageResponseSuccess(String(page), String(pageSize), listData);
});
