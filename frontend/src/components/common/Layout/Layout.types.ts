import type { ReactNode } from "react";

export interface LayoutProps {
  title: ReactNode;
  subtitle?: ReactNode;
  children: ReactNode;
}
