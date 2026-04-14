import { requestClient } from '#/api/request';

export interface AdminUserListParams {
  keyword?: string;
  page?: number;
  pageSize?: number;
  role?: string;
  status?: string;
}

export interface AdminUserListItem {
  age: number;
  bindCount: number;
  communityName: string;
  createdAt: string;
  id: string;
  lastAlertAt: string;
  name: string;
  phone: string;
  riskLevel: 'high' | 'low' | 'medium';
  riskScore: number;
  role: 'admin' | 'community' | 'elder' | 'family';
  status: 'disabled' | 'enabled';
}

export interface AdminUserListResult {
  items: AdminUserListItem[];
  total: number;
}

export async function getAdminUserListApi(params: AdminUserListParams) {
  return requestClient.get<AdminUserListResult>('/system/user/list', {
    params,
  });
}
