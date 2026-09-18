import type { CardProps } from "./Card.types";
import styles from "./Card.module.css";

export function Card({
  title,
  badge,
  tone = "default",
  children,
  className,
}: CardProps) {
  const cardClass = [
    styles.card,
    tone === "danger" ? styles["card--danger"] : null,
    className,
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <section className={cardClass}>
      {title && (
        <h2 className={styles.card__header}>
          {title}
          {badge}
        </h2>
      )}
      {children}
    </section>
  );
}
