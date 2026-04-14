import { requestClient } from '#/api/request';

export interface CommunityOverviewStat {
  description: string;
  key: string;
  trend: string;
  value: string;
}

export interface CommunityOverviewTrendItem {
  date: string;
  highRisk: number;
  visits: number;
}

export interface CommunityOverviewFocusSenior {
  disposalAdvice: string;
  elderName: string;
  id: string;
  lastAlertAt: string;
  riskLevel: 'high' | 'low' | 'medium';
  tags: string[];
}

export interface CommunityOverviewWorkorder {
  assignee: string;
  elderName: string;
  id: string;
  priority: 'high' | 'low' | 'medium';
  reason: string;
  status: 'archived' | 'processing' | 'todo';
}

export interface CommunityOverviewData {
  focusSeniors: CommunityOverviewFocusSenior[];
  riskTrend: CommunityOverviewTrendItem[];
  stats: CommunityOverviewStat[];
  todoWorkorders: CommunityOverviewWorkorder[];
}

export interface CommunityWorkorderListParams {
  keyword?: string;
  page?: number;
  pageSize?: number;
  priority?: string;
  status?: string;
}

export interface CommunityWorkorderListItem {
  assignee: string;
  createdAt: string;
  elderName: string;
  followUpAction: string;
  id: string;
  latestProgress: string;
  priority: 'high' | 'low' | 'medium';
  riskLevel: 'high' | 'low' | 'medium';
  sourceType: 'call' | 'sms';
  status: 'archived' | 'done' | 'processing' | 'todo';
  title: string;
}

export interface CommunitySeniorItem {
  collaboration: string;
  elderName: string;
  followUpStatus: string;
  id: string;
  labels: string[];
  riskLevel: 'high' | 'low' | 'medium';
}

export interface CommunityWorkorderActionItem {
  actionType: string;
  createdAt: string;
  fromStatus: string;
  id: string;
  note?: string | null;
  operatorName: string;
  toStatus: string;
}

export interface CommunityWorkorderDetail {
  actions: CommunityWorkorderActionItem[];
  assignedToName?: string | null;
  closedAt?: string | null;
  disposeMethod?: string | null;
  disposeResult?: string | null;
  elderName: string;
  id: string;
  latestAlertSummary: string;
  priority: 'high' | 'low' | 'medium';
  status: string;
  title: string;
  updatedAt: string;
  workorderNo: string;
}

export async function getCommunityOverviewApi() {
  const [elders, workorders] = await Promise.all([
    requestClient.get<any>('/community/elders', {
      params: { page: 1, page_size: 20 },
    }),
    requestClient.get<any>('/community/workorders', {
      params: { page: 1, page_size: 20 },
    }),
  ]);
  return {
    focusSeniors: elders.items.slice(0, 5).map((item: any) => ({
      disposalAdvice: `${item.follow_up_status}，建议联系${item.assigned_grid_member || '社区工作人员'}继续跟进。`,
      elderName: item.elder_name,
      id: item.elder_user_id,
      lastAlertAt: item.latest_alert_at || '-',
      riskLevel: item.risk_level,
      tags: item.tags,
    })),
    riskTrend: elders.items.slice(0, 7).map((item: any, index: number) => ({
      date: `04-${String(8 + index).padStart(2, '0')}`,
      highRisk: item.risk_level === 'high' ? 1 : 0,
      visits: item.alert_count_7d,
    })),
    stats: [
      {
        description: '重点老人',
        key: 'elders',
        trend: '来自真实社区老人接口',
        value: `${elders.pagination.total}`,
      },
      {
        description: '工单总数',
        key: 'workorders',
        trend: '可继续追踪流转状态',
        value: `${workorders.pagination.total}`,
      },
      {
        description: '高风险对象',
        key: 'highRisk',
        trend: '优先电话回访',
        value: `${elders.items.filter((item: any) => item.risk_level === 'high').length}`,
      },
      {
        description: '处理中工单',
        key: 'processing',
        trend: '继续补录处置结果',
        value: `${workorders.items.filter((item: any) => item.status === 'processing').length}`,
      },
    ],
    todoWorkorders: workorders.items.slice(0, 5).map((item: any) => ({
      assignee: item.assigned_to_name || '待分配',
      elderName: item.elder_name,
      id: item.workorder_no,
      priority: item.priority,
      reason: item.title,
      status: item.status === 'pending' ? 'todo' : item.status,
    })),
  } satisfies CommunityOverviewData;
}

export async function getCommunitySeniorListApi(params: {
  keyword?: string;
  page?: number;
  pageSize?: number;
  riskLevel?: string;
}) {
  const result = await requestClient.get<any>('/community/elders', {
    params: {
      keyword: params.keyword,
      page: params.page,
      page_size: params.pageSize,
      risk_level: params.riskLevel,
    },
  });
  return {
    items: result.items.map(
      (item: any): CommunitySeniorItem => ({
        collaboration: `已指派 ${item.assigned_grid_member}，7 日内告警 ${item.alert_count_7d} 次。`,
        elderName: item.elder_name,
        followUpStatus: item.follow_up_status,
        id: item.elder_user_id,
        labels: item.tags,
        riskLevel: item.risk_level,
      }),
    ),
    total: result.pagination.total,
  };
}

export async function getCommunityWorkorderListApi(
  params: CommunityWorkorderListParams,
) {
  const result = await requestClient.get<any>('/community/workorders', {
    params: {
      page: params.page,
      page_size: params.pageSize,
      status: params.status === 'todo' ? 'pending' : params.status,
    },
  });
  return {
    items: result.items
      .map(
        (item: any): CommunityWorkorderListItem => ({
          assignee: item.assigned_to_name || '待分配',
          createdAt: item.updated_at,
          elderName: item.elder_name,
          followUpAction: item.dispose_method || '电话回访',
          id: item.id,
          latestProgress: item.title,
          priority: item.priority,
          riskLevel: item.priority,
          sourceType: item.title.includes('短信') ? 'sms' : 'call',
          status:
            item.status === 'closed'
              ? 'archived'
              : item.status === 'pending'
                ? 'todo'
                : item.status === 'done'
                  ? 'done'
                  : 'processing',
          title: item.title,
        }),
      )
      .filter(
        (item: CommunityWorkorderListItem) =>
          !params.keyword ||
          `${item.id} ${item.title} ${item.elderName} ${item.assignee}`.includes(
            params.keyword,
          ),
      ),
    total: result.pagination.total,
  };
}

export async function getCommunityWorkorderDetailApi(workorderId: string) {
  const item = await requestClient.get<any>(`/community/workorders/${workorderId}`);
  return {
    actions: item.actions.map(
      (action: any): CommunityWorkorderActionItem => ({
        actionType: action.action_type,
        createdAt: action.created_at,
        fromStatus: action.from_status,
        id: action.id,
        note: action.note,
        operatorName: action.operator_name,
        toStatus: action.to_status,
      }),
    ),
    assignedToName: item.assigned_to_name,
    closedAt: item.closed_at,
    disposeMethod: item.dispose_method,
    disposeResult: item.dispose_result,
    elderName: item.elder_name,
    id: item.id,
    latestAlertSummary: item.latest_alert_summary,
    priority: item.priority,
    status: item.status,
    title: item.title,
    updatedAt: item.updated_at,
    workorderNo: item.workorder_no,
  } satisfies CommunityWorkorderDetail;
}

export async function transitionCommunityWorkorderApi(
  workorderId: string,
  payload: {
    actionType: string;
    assignedToUserId?: string;
    disposeMethod?: string;
    disposeResult?: string;
    note?: string;
    toStatus: string;
  },
) {
  return requestClient.post(`/community/workorders/${workorderId}/transition`, {
    action_type: payload.actionType,
    assigned_to_user_id: payload.assignedToUserId,
    dispose_method: payload.disposeMethod,
    dispose_result: payload.disposeResult,
    note: payload.note,
    to_status: payload.toStatus,
  });
}

export async function getCommunityReportApi() {
  return requestClient.get('/community/reports');
}
