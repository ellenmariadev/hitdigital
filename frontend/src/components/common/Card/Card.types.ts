import type { ReactNode } from "react";

export type CardTone = "default" | "danger";

export interface CardProps {
  title?: ReactNode;
  badge?: ReactNode;
  tone?: CardTone;
  children?: ReactNode;
  className?: string;
}
