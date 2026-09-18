import { useEffect, useState } from "react";

import { Badge, Button, Card } from "../common";
import type { FailedIdListProps } from "./FailedIdList.types";
import styles from "./FailedIdList.module.css";

const PAGE_SIZE = 100;

export function FailedIdList({ ids }: FailedIdListProps) {
  const [visibleCount, setVisibleCount] = useState(PAGE_SIZE);

  useEffect(() => {
    setVisibleCount(PAGE_SIZE);
  }, [ids]);

  const visibleIds = ids.slice(0, visibleCount);
  const remaining = ids.length - visibleIds.length;

  return (
    <Card
      title="IDs que falharam"
      tone={ids.length > 0 ? "danger" : "default"}
      badge={
        <Badge tone={ids.length > 0 ? "danger" : "info"}>{ids.length}</Badge>
      }
    >
      {ids.length === 0 ? (
        <p className={styles.empty}>Nenhuma falha.</p>
      ) : (
        <>
          <ul className={styles["id-list"]}>
            {visibleIds.map((id) => (
              <li key={id} className={styles["id-list__item"]}>
                <Badge tone="danger" className={styles["id-list__badge"]}>
                  {id}
                </Badge>
              </li>
            ))}
          </ul>
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
