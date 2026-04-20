import type { UserRole } from '@/types/app'

const roleHomeMap: Record<UserRole, string> = {
  elder: '/pages/elder/home',
  guardian: '/pages/guardian/home'
}

export function navigateToRoleHome(role: UserRole, redirect = false) {
  const url = roleHomeMap[role]

  if (redirect) {
    uni.redirectTo({ url })
    return
  }

  uni.navigateTo({ url })
}

export function openPage(url: string) {
  uni.navigateTo({ url })
}

export function relaunchTo(url: string) {
  uni.reLaunch({ url })
}

export function backPage(delta = 1) {
  uni.navigateBack({ delta })
}
