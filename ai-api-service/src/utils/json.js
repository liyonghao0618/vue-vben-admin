export function safeJsonParse(value) {
  try {
    return { data: JSON.parse(value), ok: true };
  } catch {
    return { data: null, ok: false };
  }
}

function extractJsonFromCodeBlock(value) {
  const match = value.match(/```(?:json)?\s*([\s\S]*?)\s*```/u);
  return match?.[1]?.trim() || '';
}

function extractBalancedJsonObject(value) {
  const start = value.indexOf('{');
  if (start === -1) {
    return '';
  }

  let depth = 0;
  let inString = false;
  let escaped = false;

  for (let index = start; index < value.length; index += 1) {
    const char = value[index];

    if (escaped) {
      escaped = false;
      continue;
    }

    if (char === '\\') {
      escaped = true;
      continue;
    }

    if (char === '"') {
      inString = !inString;
      continue;
    }

    if (inString) {
      continue;
    }

    if (char === '{') {
      depth += 1;
    } else if (char === '}') {
      depth -= 1;
      if (depth === 0) {
        return value.slice(start, index + 1);
      }
    }
  }

  return '';
}

export function safeStructuredJsonParse(value) {
  const direct = safeJsonParse(value);
  if (direct.ok) {
    return direct;
  }

  const fromCodeBlock = extractJsonFromCodeBlock(value);
  if (fromCodeBlock) {
    const codeBlockParsed = safeJsonParse(fromCodeBlock);
    if (codeBlockParsed.ok) {
      return codeBlockParsed;
    }
  }

  const fromBalancedObject = extractBalancedJsonObject(value);
  if (fromBalancedObject) {
    const balancedParsed = safeJsonParse(fromBalancedObject);
    if (balancedParsed.ok) {
      return balancedParsed;
    }
  }

  return { data: null, ok: false };
}
