import type { BadgeProps } from "./Badge.types";
import styles from "./Badge.module.css";

const TONE_CLASS: Record<NonNullable<BadgeProps["tone"]>, string> = {
  info: styles.info,
  danger: styles.danger,
  neutral: styles.neutral,
  purple: styles.purple,
  green: styles.green,
};

export function Badge({ tone = "info", children, className }: BadgeProps) {
  return (
    <span
      className={[styles.badge, TONE_CLASS[tone], className]
        .filter(Boolean)
        .join(" ")}
    >
      {children}
    </span>
  );
}
