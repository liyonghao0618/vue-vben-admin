<script lang="ts" setup>
import type { VbenFormSchema } from '@vben/common-ui';
import type { Recordable } from '@vben/types';

import { computed, h, ref } from 'vue';

import { AuthenticationRegister, z } from '@vben/common-ui';
import { $t } from '@vben/locales';
import { message } from 'ant-design-vue';

import { registerApi } from '#/api';

defineOptions({ name: 'Register' });

const loading = ref(false);

const roleOptions = [
  { label: '老年用户', value: 'elder' },
  { label: '子女用户', value: 'family' },
  { label: '社区工作人员', value: 'community' },
  { label: '系统管理员', value: 'admin' },
] as const;

const formSchema = computed((): VbenFormSchema[] => {
  return [
    {
      component: 'Select',
      componentProps: {
        options: roleOptions,
        placeholder: '请选择身份',
      },
      defaultValue: 'elder',
      fieldName: 'role',
      label: '身份类型',
      rules: z.string().min(1, { message: '请选择身份类型' }),
    },
    {
      component: 'VbenInput',
      componentProps: {
        placeholder: '请输入姓名或昵称',
      },
      fieldName: 'displayName',
      label: '姓名',
      rules: z.string().min(1, { message: '请输入姓名' }),
    },
    {
      component: 'VbenInput',
      componentProps: {
        placeholder: '请输入手机号',
      },
      fieldName: 'phone',
      label: '手机号',
      rules: z.string().min(6, { message: '请输入手机号' }),
    },
    {
      component: 'VbenInput',
      componentProps: {
        placeholder: $t('authentication.usernameTip'),
      },
      fieldName: 'username',
      label: $t('authentication.username'),
      rules: z.string().min(1, { message: $t('authentication.usernameTip') }),
    },
    {
      component: 'VbenInputPassword',
      componentProps: {
        passwordStrength: true,
        placeholder: $t('authentication.password'),
      },
      fieldName: 'password',
      label: $t('authentication.password'),
      renderComponentContent() {
        return {
          strengthText: () => $t('authentication.passwordStrength'),
        };
      },
      rules: z.string().min(1, { message: $t('authentication.passwordTip') }),
    },
    {
      component: 'VbenInputPassword',
      componentProps: {
        placeholder: $t('authentication.confirmPassword'),
      },
      dependencies: {
        rules(values) {
          const { password } = values;
          return z
            .string({ required_error: $t('authentication.passwordTip') })
            .min(1, { message: $t('authentication.passwordTip') })
            .refine((value) => value === password, {
              message: $t('authentication.confirmPasswordTip'),
            });
        },
        triggerFields: ['password'],
      },
      fieldName: 'confirmPassword',
      label: $t('authentication.confirmPassword'),
    },
    {
      component: 'VbenInput',
      componentProps: {
        placeholder: '老年/子女/社区用户可填写邀请码',
      },
      fieldName: 'inviteCode',
      help: '用于模拟“邀请码加入”流程，管理员可留空。',
      label: '邀请码',
    },
    {
      component: 'VbenCheckbox',
      fieldName: 'agreePolicy',
      renderComponentContent: () => ({
        default: () =>
          h('span', [
            $t('authentication.agree'),
            h(
              'a',
              {
                class: 'vben-link ml-1 ',
                href: '',
              },
              `${$t('authentication.privacyPolicy')} & ${$t('authentication.terms')}`,
            ),
          ]),
      }),
      rules: z.boolean().refine((value) => !!value, {
        message: $t('authentication.agreeTip'),
      }),
    },
  ];
});

async function handleSubmit(value: Recordable<any>) {
  loading.value = true;
  try {
    await registerApi({
      displayName: value.displayName,
      inviteCode: value.inviteCode || undefined,
      password: value.password,
      phone: value.phone,
      role: value.role,
      username: value.username,
    });
    message.success('注册成功，请返回登录页使用新账号登录');
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <AuthenticationRegister
    :form-schema="formSchema"
    :loading="loading"
    @submit="handleSubmit"
  />
</template>
