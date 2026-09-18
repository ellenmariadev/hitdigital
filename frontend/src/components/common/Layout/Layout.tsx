import type { LayoutProps } from "./Layout.types";
import styles from "./Layout.module.css";

export function Layout({ title, subtitle, children }: LayoutProps) {
  return (
    <main className={styles.page}>
      <header>
        <h1 className={styles.header__title}>{title}</h1>
        {subtitle && <p className={styles.header__subtitle}>{subtitle}</p>}
      </header>
      {children}
    </main>
  );
}
