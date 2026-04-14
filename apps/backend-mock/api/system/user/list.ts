import { eventHandler, getQuery } from 'h3';

import { verifyAccessToken } from '~/utils/jwt-utils';
import {
  sleep,
  unAuthorizedResponse,
  usePageResponseSuccess,
} from '~/utils/response';

interface UserListItem {
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

const MOCK_USER_LIST: UserListItem[] = [
  {
    age: 68,
    bindCount: 2,
    communityName: '松柏社区',
    createdAt: '2026-03-18 10:20',
    id: 'USR-1001',
    lastAlertAt: '2026-04-14 09:15',
    name: '王阿姨',
    phone: '13800000001',
    riskLevel: 'high',
    riskScore: 92,
    role: 'elder',
    status: 'enabled',
  },
  {
    age: 42,
    bindCount: 1,
    communityName: '松柏社区',
    createdAt: '2026-03-18 10:30',
    id: 'USR-1002',
    lastAlertAt: '2026-04-14 09:20',
    name: '李晓华',
    phone: '13800000002',
    riskLevel: 'medium',
    riskScore: 64,
    role: 'family',
    status: 'enabled',
  },
  {
    age: 36,
    bindCount: 0,
    communityName: '康宁社区',
    createdAt: '2026-03-15 14:40',
    id: 'USR-1003',
    lastAlertAt: '2026-04-14 08:45',
    name: '张海宁',
    phone: '13800000003',
    riskLevel: 'medium',
    riskScore: 58,
    role: 'community',
    status: 'enabled',
  },
  {
    age: 33,
    bindCount: 0,
    communityName: '平台运营中心',
    createdAt: '2026-03-10 09:00',
    id: 'USR-1004',
    lastAlertAt: '2026-04-13 20:10',
    name: '系统管理员',
    phone: '13800000004',
    riskLevel: 'low',
    riskScore: 18,
    role: 'admin',
    status: 'enabled',
  },
  {
    age: 73,
    bindCount: 3,
    communityName: '康宁社区',
    createdAt: '2026-03-09 12:22',
    id: 'USR-1005',
    lastAlertAt: '2026-04-13 17:40',
    name: '周奶奶',
    phone: '13800000005',
    riskLevel: 'high',
    riskScore: 88,
    role: 'elder',
    status: 'enabled',
  },
  {
    age: 45,
    bindCount: 2,
    communityName: '康宁社区',
    createdAt: '2026-03-09 12:30',
    id: 'USR-1006',
    lastAlertAt: '2026-04-13 17:42',
    name: '陈志强',
    phone: '13800000006',
    riskLevel: 'medium',
    riskScore: 61,
    role: 'family',
    status: 'enabled',
  },
  {
    age: 58,
    bindCount: 0,
    communityName: '海棠社区',
    createdAt: '2026-03-05 15:10',
    id: 'USR-1007',
    lastAlertAt: '2026-04-12 16:08',
    name: '赵桂兰',
    phone: '13800000007',
    riskLevel: 'low',
    riskScore: 22,
    role: 'elder',
    status: 'disabled',
  },
  {
    age: 39,
    bindCount: 0,
    communityName: '海棠社区',
    createdAt: '2026-03-04 11:20',
    id: 'USR-1008',
    lastAlertAt: '2026-04-12 15:18',
    name: '刘晓燕',
    phone: '13800000008',
    riskLevel: 'low',
    riskScore: 16,
    role: 'community',
    status: 'enabled',
  },
  {
    age: 70,
    bindCount: 1,
    communityName: '松柏社区',
    createdAt: '2026-03-02 10:05',
    id: 'USR-1009',
    lastAlertAt: '2026-04-11 14:26',
    name: '孙大爷',
    phone: '13800000009',
    riskLevel: 'medium',
    riskScore: 54,
    role: 'elder',
    status: 'enabled',
  },
  {
    age: 41,
    bindCount: 1,
    communityName: '松柏社区',
    createdAt: '2026-03-02 10:08',
    id: 'USR-1010',
    lastAlertAt: '2026-04-11 14:28',
    name: '孙悦',
    phone: '13800000010',
    riskLevel: 'medium',
    riskScore: 49,
    role: 'family',
    status: 'enabled',
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
    50,
    Math.max(
      1,
      Number.parseInt(normalizeQueryValue(query.pageSize) || '10', 10) || 10,
    ),
  );
  const keyword = (normalizeQueryValue(query.keyword) || '').toLowerCase();
  const role = normalizeQueryValue(query.role);
  const status = normalizeQueryValue(query.status);

  let listData = structuredClone(MOCK_USER_LIST);

  if (keyword) {
    listData = listData.filter((item) =>
      [item.id, item.name, item.phone, item.communityName].some((field) =>
        field.toLowerCase().includes(keyword),
      ),
    );
  }

  if (role) {
    listData = listData.filter((item) => item.role === role);
  }

  if (status) {
    listData = listData.filter((item) => item.status === status);
  }

  return usePageResponseSuccess(String(page), String(pageSize), listData);
});
