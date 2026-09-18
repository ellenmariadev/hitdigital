export interface User {
  id: number;
  name: string;
  email?: string | null;
  username?: string | null;
}

export interface FetchUsersResponse {
  users: User[];
  failed: number[];
}
