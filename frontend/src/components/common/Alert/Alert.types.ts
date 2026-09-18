import type { ReactNode } from "react";

export type AlertTone = "error" | "info" | "success";

export interface AlertProps {
  tone?: AlertTone;
  title?: ReactNode;
  children?: ReactNode;
  className?: string;
}
