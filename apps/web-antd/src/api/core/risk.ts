import { requestClient } from '#/api/request';

export interface RiskAlertListParams {
  page?: number;
  pageSize?: number;
  riskLevel?: string;
  sourceType?: string;
  status?: string;
}

export interface RiskAlertItem {
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

export interface RiskAlertListResult {
  items: RiskAlertItem[];
  total: number;
}

export async function getRiskAlertListApi(params: RiskAlertListParams) {
  return requestClient.get<RiskAlertListResult>('/risk/alerts/list', {
    params,
  });
}
