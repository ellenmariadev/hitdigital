import { memo, useEffect, useRef, useState } from "react";

import { Badge, Button, Icon } from "../common";
import type { BadgeTone } from "../common/Badge/Badge.types";
import { USER_PROVIDER_URL } from "../../config/env";
import type { UserCardProps } from "./UserCard.types";
import styles from "./UserCard.module.css";

const TAG_TONES: BadgeTone[] = ["neutral", "purple", "green", "danger"];

type CopiedField = "email" | "username" | null;

async function copyToClipboard(text: string): Promise<void> {
  if (navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(text);
    return;
  }
  const textarea = document.createElement("textarea");
  textarea.value = text;
  document.body.appendChild(textarea);
  textarea.select();
  document.execCommand("copy");
  document.body.removeChild(textarea);
}

export const UserCard = memo(function UserCard({ user }: UserCardProps) {
  const [copied, setCopied] = useState<CopiedField>(null);
  const timeoutRef = useRef<number | null>(null);

  useEffect(
    () => () => {
      if (timeoutRef.current !== null) {
        window.clearTimeout(timeoutRef.current);
      }
    },
    [],
  );

  const handleCopy = async (field: Exclude<CopiedField, null>, value: string) => {
    try {
      await copyToClipboard(value);
      setCopied(field);
      if (timeoutRef.current !== null) {
        window.clearTimeout(timeoutRef.current);
      }
      timeoutRef.current = window.setTimeout(() => setCopied(null), 1500);
    } catch {
      setCopied(null);
    }
  };

  const tagTone = TAG_TONES[user.id % TAG_TONES.length];

  return (
    <article className={styles.card}>
      {copied && <span className={styles.copied}>Copiado!</span>}

      <div className={styles.header}>
        <h3 className={styles.name}>{user.name}</h3>
      </div>

      <p className={styles.email}>{user.email ?? "—"}</p>

      <span className={styles.username}>
        {user.username ? `@${user.username}` : "—"}
      </span>

      <div className={styles.actions}>
        <a
          className={styles.iconLink}
          title="Abrir no provider"
          aria-label="Abrir no provider"
          href={`${USER_PROVIDER_URL}/${user.id}`}
          target="_blank"
          rel="noreferrer"
        >
          <Icon name="play" size={14} />
        </a>
        <Button
          variant="icon"
          title="Copiar username"
          aria-label="Copiar username"
          onClick={() => user.username && handleCopy("username", user.username)}
        >
          <Icon name="copy" size={14} />
        </Button>
      </div>

      <Badge tone={tagTone} className={styles.tag}>
        #{user.id}
      </Badge>
    </article>
  );
});
