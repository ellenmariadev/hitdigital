import { useEffect, useState } from "react";

import { Badge, Button, Card } from "../common";
import { UserCard } from "../UserCard";
import type { UserCardListProps } from "./UserCardList.types";
import styles from "./UserCardList.module.css";

const PAGE_SIZE = 60;

export function UserCardList({ users }: UserCardListProps) {
  const [visibleCount, setVisibleCount] = useState(PAGE_SIZE);

  useEffect(() => {
    setVisibleCount(PAGE_SIZE);
  }, [users]);

  const visibleUsers = users.slice(0, visibleCount);
  const remaining = users.length - visibleUsers.length;

  return (
    <Card
      title="Usuários encontrados"
      badge={<Badge>{users.length}</Badge>}
    >
      {users.length === 0 ? (
        <p className={styles.empty}>Nenhum usuário encontrado.</p>
      ) : (
        <>
          <p className={styles.summary}>
            exibindo {visibleUsers.length} de {users.length}{" "}
            {users.length === 1 ? "usuário" : "usuários"}
          </p>
          <div className={styles.grid}>
            {visibleUsers.map((user) => (
              <UserCard key={user.id} user={user} />
            ))}
          </div>
          {remaining > 0 && (
            <Button
              variant="ghost"
              className={styles.more}
              onClick={() => setVisibleCount((count) => count + PAGE_SIZE)}
            >
              Mostrar mais ({remaining} restantes)
            </Button>
          )}
        </>
      )}
    </Card>
  );
}
