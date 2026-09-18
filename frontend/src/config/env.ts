export const API_BASE_URL: string = import.meta.env.VITE_API_BASE_URL ?? "";

export const USER_PROVIDER_URL: string =
  import.meta.env.VITE_USER_PROVIDER_URL ??
  "https://jsonplaceholder.typicode.com/users";

export const MAX_USER_IDS: number = Number(
  import.meta.env.VITE_MAX_USER_IDS ?? 500,
);
