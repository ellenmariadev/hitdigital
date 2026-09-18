import type { FetchUsersResponse } from "../types/user";
import { API_BASE_URL } from "../config/env";
import { ApiError } from "./errors";

function extractErrorDetail(body: unknown): string | null {
  if (typeof body !== "object" || body === null || !("detail" in body)) {
    return null;
  }

  const detail = (body as { detail: unknown }).detail;
  if (typeof detail === "string") {
    return detail;
  }

  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) => {
        if (typeof item === "object" && item !== null && "msg" in item) {
          return String((item as { msg: unknown }).msg);
        }
        return String(item);
      })
      .filter(Boolean);
    if (messages.length > 0) {
      return messages.join("; ");
    }
  }

  return null;
}

export async function fetchUsers(
  userIds: number[],
): Promise<FetchUsersResponse> {
  let response: Response;

  try {
    response = await fetch(`${API_BASE_URL}/api/users/fetch`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ user_ids: userIds }),
    });
  } catch {
    throw new ApiError(
      "Não foi possível conectar ao servidor. Verifique se o backend está no ar.",
      null,
    );
  }

  if (!response.ok) {
    let detail: string | null = null;
    try {
      detail = extractErrorDetail(await response.json());
    } catch {
      detail = null;
    }
    throw new ApiError(
      detail ?? `O backend respondeu com erro ${response.status}.`,
      response.status,
    );
  }

  return (await response.json()) as FetchUsersResponse;
}
