import { requestClient } from '#/api/request';

export interface RolePermissionOverviewItem {
  codeCount: number;
  description: string;
  menuCount: number;
  menus: string[];
  name: string;
  resources: string[];
  role: 'admin' | 'community' | 'elder' | 'family';
  scope: string;
}

export async function getRolePermissionOverviewApi() {
  return requestClient.get<RolePermissionOverviewItem[]>(
    '/system/role/permission-overview',
  );
}
