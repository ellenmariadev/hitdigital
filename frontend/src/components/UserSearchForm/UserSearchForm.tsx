import { Button, Card, Icon } from "../common";
import type { UserSearchFormProps } from "./UserSearchForm.types";
import styles from "./UserSearchForm.module.css";

export function UserSearchForm({
  value,
  isSearching,
  validationError,
  idCount,
  maxUserIds,
  onChange,
  onSearch,
}: UserSearchFormProps) {
  return (
    <Card>
      <form
        className={styles.form}
        onSubmit={(event) => {
          event.preventDefault();
          onSearch();
        }}
      >
        <label className={styles.field__label} htmlFor="user-ids-input">
          IDs dos usuários
        </label>
        <div className={styles.field}>
          <span className={styles.field__icon} aria-hidden="true">
            <Icon name="search" size={16} />
          </span>
          <textarea
            id="user-ids-input"
            className={styles.field__textarea}
            rows={4}
            placeholder="Ex.: 1, 2, 3, 999"
            value={value}
            onChange={(event) => onChange(event.target.value)}
            disabled={isSearching}
          />
        </div>
        <p className={styles.field__hint}>
          Separe os IDs por vírgula, espaço ou quebra de linha.
          {idCount > 0 && (
            <span className={styles.field__count}>
              {" "}
              · {idCount} {idCount === 1 ? "ID" : "IDs"} · máx. {maxUserIds}
            </span>
          )}
        </p>
        {validationError && (
          <p className={styles.field__error} role="alert">
            {validationError}
          </p>
        )}
        <Button type="submit" disabled={isSearching}>
          {isSearching ? "Consultando..." : "Consultar"}
        </Button>
      </form>
    </Card>
  );
}
