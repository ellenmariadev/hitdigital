import type { ReactNode } from "react";

export type BadgeTone = "info" | "danger" | "neutral" | "purple" | "green";

export interface BadgeProps {
  tone?: BadgeTone;
  children: ReactNode;
  className?: string;
}
