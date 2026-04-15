import { requestClient } from '#/api/request';

import { getRiskAlertListApi } from './risk';

export interface FamilyOverviewStat {
  description: string;
  key: string;
  trend: string;
  value: string;
}

export interface FamilyOverviewAlertTrendItem {
  date: string;
  total: number;
}

export interface FamilyOverviewRiskDistributionItem {
  count: number;
  label: string;
}

export interface FamilyOverviewFocusItem {
  currentStatus: string;
  elderName: string;
  id: string;
  lastAlertAt: string;
  riskLevel: 'high' | 'low' | 'medium';
  riskSummary: string;
}

export interface FamilyOverviewData {
  alertTrend: FamilyOverviewAlertTrendItem[];
  focusList: FamilyOverviewFocusItem[];
  riskDistribution: FamilyOverviewRiskDistributionItem[];
  stats: FamilyOverviewStat[];
}

export interface FamilyAlertListParams {
  page?: number;
  pageSize?: number;
  readStatus?: string;
  riskLevel?: string;
  status?: string;
}

export interface FamilyAlertItem {
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

export interface FamilyNotificationItem {
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

export interface FamilyNotificationListParams {
  page?: number;
  pageSize?: number;
  readStatus?: string;
  riskLevel?: string;
  status?: string;
}

export async function getFamilyOverviewApi() {
  const [bindings, alerts] = await Promise.all([
    requestClient.get<any[]>('/bindings'),
    getRiskAlertListApi({ page: 1, pageSize: 50 }),
  ]);
  const riskDistribution = [
    {
      count: alerts.items.filter(
        (item: { riskLevel: string }) => item.riskLevel === 'high',
      ).length,
      label: '高风险',
    },
    {
      count: alerts.items.filter(
        (item: { riskLevel: string }) => item.riskLevel === 'medium',
      ).length,
      label: '中风险',
    },
    {
      count: alerts.items.filter(
        (item: { riskLevel: string }) => item.riskLevel === 'low',
      ).length,
      label: '低风险',
    },
  ];
  const highRiskCount =
    riskDistribution.find((item) => item.label === '高风险')?.count ?? 0;
  return {
    alertTrend: alerts.items
      .slice(0, 7)
      .map((item: { occurredAt: string }) => ({
        date: item.occurredAt.slice(5, 10),
        total: 1,
      })),
    focusList: alerts.items.slice(0, 5).map((item: FamilyAlertItem | any) => ({
      currentStatus: item.status === 'pending' ? '待跟进' : '已处理',
      elderName: item.elderName,
      id: item.id,
      lastAlertAt: item.occurredAt,
      riskLevel: item.riskLevel,
      riskSummary: item.hitReason,
    })),
    riskDistribution,
    stats: [
      {
        description: '已绑定老人',
        key: 'bindings',
        trend: '监护关系已接真实绑定数据',
        value: `${bindings.length}`,
      },
      {
        description: '风险事件',
        key: 'alerts',
        trend: '来自真实风险告警接口',
        value: `${alerts.total}`,
      },
      {
        description: '高风险',
        key: 'high',
        trend: '优先联系老人并核实',
        value: `${highRiskCount}`,
      },
      {
        description: '待跟进',
        key: 'pending',
        trend: '继续查看通知与提醒发送',
        value: `${alerts.items.filter((item: { status: string }) => item.status === 'pending').length}`,
      },
    ],
  } satisfies FamilyOverviewData;
}

export async function getFamilyAlertListApi(params: FamilyAlertListParams) {
  const alerts = await getRiskAlertListApi({
    page: params.page,
    pageSize: params.pageSize,
    riskLevel: params.riskLevel,
  });
  return {
    items: alerts.items
      .map(
        (item: (typeof alerts.items)[number]): FamilyAlertItem => ({
          advice: item.advice,
          contactSuggestion: item.contactSuggestion,
          elderName: item.elderName,
          handledAt: item.status === 'handled' ? item.occurredAt : undefined,
          hitReason: item.hitReason,
          id: item.id,
          occurredAt: item.occurredAt,
          readStatus: 'unread',
          remoteMessage: '先不要转账，我马上联系您核实。',
          riskLevel: item.riskLevel,
          riskScore: item.riskScore,
          sourceType: item.sourceType,
          status: item.status,
          title: item.title,
        }),
      )
      .filter(
        (item: FamilyAlertItem) =>
          !params.status || item.status === params.status,
      ),
    total: alerts.total,
  };
}

export async function getFamilyNotificationListApi(
  params: FamilyNotificationListParams,
) {
  const result = await requestClient.get<any>('/notifications', {
    params: {
      is_read: params.readStatus ? params.readStatus === 'read' : undefined,
      page: params.page,
      page_size: params.pageSize,
    },
  });

  return {
    items: result.items
      .map(
        (item: any): FamilyNotificationItem => ({
          channel:
            item.channel === 'voice'
              ? 'voice'
              : item.channel === 'sms'
                ? 'sms'
                : 'app',
          elderName: item.elder_name,
          id: item.id,
          notifiedAt: item.sent_at,
          operatorName: item.receiver_name,
          readStatus: item.is_read ? 'read' : 'unread',
          relatedAlertTitle: item.alert_title,
          result:
            item.status === 'failed'
              ? 'failed'
              : item.status === 'pending'
                ? 'processing'
                : 'delivered',
          riskLevel: item.risk_level,
          status: item.is_read ? 'closed' : 'pending',
        }),
      )
      .filter(
        (item: FamilyNotificationItem) =>
          !params.riskLevel || item.riskLevel === params.riskLevel,
      )
      .filter(
        (item: FamilyNotificationItem) =>
          !params.status || item.status === params.status,
      ),
    total: result.pagination.total,
  };
}

export async function markFamilyNotificationReadApi(notificationId: string) {
  return (requestClient as any).patch(`/notifications/${notificationId}/read`);
}

export async function sendFamilyReminderApi(payload: {
  channel: string;
  content: string;
  elderUserId: string;
}) {
  return requestClient.post('/family/reminders', {
    channel: payload.channel,
    content: payload.content,
    elder_user_id: payload.elderUserId,
  });
}
