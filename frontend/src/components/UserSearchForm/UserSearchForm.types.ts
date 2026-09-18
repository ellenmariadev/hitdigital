export interface UserSearchFormProps {
  value: string;
  isSearching: boolean;
  validationError: string | null;
  idCount: number;
  maxUserIds: number;
  onChange: (value: string) => void;
  onSearch: () => void;
}
