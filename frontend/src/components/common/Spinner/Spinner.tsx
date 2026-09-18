import type { SpinnerProps } from "./Spinner.types";
import styles from "./Spinner.module.css";

export function Spinner({ label, className }: SpinnerProps) {
  return (
    <div
      className={[styles.wrapper, className].filter(Boolean).join(" ")}
      role="status"
      aria-live="polite"
    >
      <span className={styles.circle} aria-hidden="true" />
      {label}
    </div>
  );
}
