import { MAX_USER_IDS } from "../config/env";

export interface ParsedUserIds {
  ids: number[];
  error: string | null;
}

export function parseUserIds(
  rawInput: string,
  maxUserIds: number = MAX_USER_IDS,
): ParsedUserIds {
  const tokens = rawInput
    .split(/[\s,;]+/)
    .map((token) => token.trim())
    .filter((token) => token.length > 0);

  if (tokens.length === 0) {
    return { ids: [], error: "Informe ao menos um ID." };
  }

  const ids: number[] = [];
  const seen = new Set<number>();

  for (const token of tokens) {
    if (!/^\d+$/.test(token)) {
      return { ids: [], error: `"${token}" não é um ID inteiro válido.` };
    }
    const value = Number(token);
    if (value <= 0) {
      return { ids: [], error: "Os IDs devem ser inteiros positivos." };
    }
    if (!seen.has(value)) {
      seen.add(value);
      ids.push(value);
    }
  }

  if (ids.length > maxUserIds) {
    return {
      ids: [],
      error: `Máximo de ${maxUserIds} IDs por consulta (você informou ${ids.length}).`,
    };
  }

  return { ids, error: null };
}
