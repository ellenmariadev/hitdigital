import type { ButtonProps, ButtonVariant } from "./Button.types";
import styles from "./Button.module.css";

const VARIANT_CLASS: Record<ButtonVariant, string> = {
  primary: styles.primary,
  ghost: styles.ghost,
  icon: styles.icon,
};

export function Button({
  variant = "primary",
  className,
  type = "button",
  ...rest
}: ButtonProps) {
  return (
    <button
      type={type}
      className={[styles.button, VARIANT_CLASS[variant], className]
        .filter(Boolean)
        .join(" ")}
      {...rest}
    />
  );
}
