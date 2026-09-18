import type { ButtonHTMLAttributes } from "react";

export type ButtonVariant = "primary" | "ghost" | "icon";

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
}
