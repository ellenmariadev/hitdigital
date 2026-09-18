import { useCallback, useState } from "react";

import { fetchUsers } from "../api/userApi";
import { ApiError } from "../api/errors";
import type { FetchUsersResponse } from "../types/user";

export type SearchStatus = "idle" | "loading" | "success" | "error";

export interface UseUserSearchResult {
  status: SearchStatus;
  data: FetchUsersResponse | null;
  backendError: string | null;
  search: (userIds: number[]) => Promise<void>;
}

export function useUserSearch(): UseUserSearchResult {
  const [status, setStatus] = useState<SearchStatus>("idle");
  const [data, setData] = useState<FetchUsersResponse | null>(null);
  const [backendError, setBackendError] = useState<string | null>(null);

  const search = useCallback(async (userIds: number[]) => {
    setStatus("loading");
    setData(null);
    setBackendError(null);

    try {
      setData(await fetchUsers(userIds));
      setStatus("success");
    } catch (caught) {
      setBackendError(
        caught instanceof ApiError
          ? caught.message
          : "Erro inesperado ao consultar o backend.",
      );
      setStatus("error");
    }
  }, []);

  return { status, data, backendError, search };
}
