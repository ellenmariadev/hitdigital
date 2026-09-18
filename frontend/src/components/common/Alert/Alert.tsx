import type { AlertProps } from "./Alert.types";
import styles from "./Alert.module.css";

export function Alert({
  tone = "info",
  title,
  children,
  className,
}: AlertProps) {
  const toneClass =
    tone === "error" ? styles.error : tone === "success" ? styles.success : styles.info;

  return (
    <div
      role={tone === "error" ? "alert" : "status"}
      className={[styles.alert, toneClass, className].filter(Boolean).join(" ")}
    >
      {title && <strong>{title} </strong>}
      {children}
    </div>
  );
}
