import type { UserInfo } from '@vben/types';

import { requestClient } from '#/api/request';

/**
 * 获取用户信息
 */
export async function getUserInfoApi() {
  const result = await requestClient.get<{
    display_name: string;
    permissions: string[];
    phone: string;
    roles: string[];
    user_id: string;
    username: string;
  }>('/auth/me');

  const firstRole = result.roles[0] ?? 'elder';
  const homePathMap: Record<string, string> = {
    admin: '/admin/users',
    community: '/community/workorders',
    elder: '/elder/home',
    family: '/family/notifications',
  };

  return {
    avatar: '',
    desc: result.phone,
    homePath: homePathMap[firstRole] ?? '/elder/home',
    realName: result.display_name,
    roles: result.roles,
    token: '',
    userId: result.user_id,
    username: result.username,
  } satisfies UserInfo;
}
