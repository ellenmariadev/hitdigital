/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string;
  readonly VITE_USER_PROVIDER_URL?: string;
  readonly VITE_MAX_USER_IDS?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
