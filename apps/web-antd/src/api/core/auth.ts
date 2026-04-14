import { baseRequestClient, requestClient } from '#/api/request';

export namespace AuthApi {
  /** 登录接口参数 */
  export interface LoginParams {
    password?: string;
    username?: string;
  }

  /** 登录接口返回值 */
  export interface LoginResult {
    accessToken: string;
  }

  export interface RefreshTokenResult {
    accessToken: string;
  }
}

/**
 * 登录
 */
export async function loginApi(data: AuthApi.LoginParams) {
  const result = await requestClient.post<{
    access_token: string;
  }>('/auth/login', data);
  return {
    accessToken: result.access_token,
  };
}

/**
 * 刷新accessToken
 */
export async function refreshTokenApi() {
  const result = await requestClient.post<{
    access_token: string;
  }>('/auth/refresh', {});
  return {
    accessToken: result.access_token,
  };
}

/**
 * 退出登录
 */
export async function logoutApi() {
  return baseRequestClient.post('/auth/logout', {
    withCredentials: true,
  });
}

/**
 * 获取用户权限码
 */
export async function getAccessCodesApi() {
  const roles = await requestClient.get<
    Array<{
      code: string;
      permissions: string[];
    }>
  >('/auth/roles');
  return roles.flatMap((item) => item.permissions);
}
