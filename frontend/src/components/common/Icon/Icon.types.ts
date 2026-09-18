export type IconName =
  | "settings"
  | "play"
  | "chat"
  | "copy"
  | "search"
  | "external";

export interface IconProps {
  name: IconName;
  size?: number;
  className?: string;
  title?: string;
}
