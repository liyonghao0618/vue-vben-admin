export function buildFraudDetectionPrompt({ text, scene = 'generic', source = 'unknown' }) {
  return [
    '你是一个诈骗识别助手，负责分析输入文本是否存在诈骗风险。',
    '请重点关注以下信号：冒充客服、刷单返利、投资理财诱导、中奖补贴诱导、钓鱼链接、索取验证码、要求转账、诱导下载陌生 App、索取身份证或银行卡信息。',
    '输出必须是严格 JSON，不要输出 Markdown，不要输出解释，不要输出代码块。',
    'JSON 对象字段固定为：isFraud, riskLevel, category, reason, evidence, suggestion。',
    'riskLevel 只能是 low、medium、high。',
    'category 使用英文短语，例如 impersonation-support、task-rebate、fake-investment、prize-subsidy、phishing-link、verification-code、transfer-request、download-app、identity-collection、safe。',
    'reason 用一句简洁中文概括判定原因。',
    'evidence 是字符串数组，列出命中的关键可疑片段。',
    'suggestion 用一句简洁中文给出处理建议。',
    `场景: ${scene}`,
    `来源: ${source}`,
    `待分析文本: ${text}`
  ].join('\n');
}
