import { useMemo, useState } from "react";

import { Alert, Layout, Spinner } from "./components/common";
import { FailedIdList } from "./components/FailedIdList";
import { UserCardList } from "./components/UserCardList";
import { UserSearchForm } from "./components/UserSearchForm";
import { MAX_USER_IDS } from "./config/env";
import { useElapsedSeconds } from "./hooks/useElapsedSeconds";
import { useUserSearch } from "./hooks/useUserSearch";
import styles from "./App.module.css";
import { parseUserIds } from "./utils/parseUserIds";

const DEFAULT_IDS_INPUT = "1, 2, 3, 999";

export default function App() {
  const [idsInput, setIdsInput] = useState(DEFAULT_IDS_INPUT);
  const [validationError, setValidationError] = useState<string | null>(null);
  const { status, data, backendError, search } = useUserSearch();

  const isSearching = status === "loading";
  const elapsedSeconds = useElapsedSeconds(isSearching);

  const idCount = useMemo(
    () => parseUserIds(idsInput).ids.length,
    [idsInput],
  );

  const handleSearch = () => {
    const { ids, error } = parseUserIds(idsInput);
    setValidationError(error);
    if (error) {
      return;
    }
    void search(ids);
  };

  return (
    <Layout
      title="HitDigital"
      subtitle={
        <>
          Informe os IDs e consulte o backend em{" "}
          <code>POST /api/users/fetch</code>.
        </>
      }
    >
      <UserSearchForm
        value={idsInput}
        isSearching={isSearching}
        validationError={validationError}
        idCount={idCount}
        maxUserIds={MAX_USER_IDS}
        onChange={setIdsInput}
        onSearch={handleSearch}
      />

      {isSearching && (
        <Spinner
          label={`Consultando ${idCount} ${
            idCount === 1 ? "usuário" : "usuários"
          }... ${elapsedSeconds}s`}
        />
      )}

      {status === "error" && backendError && (
        <Alert tone="error" title="Erro do backend:">
          {backendError}
        </Alert>
      )}

      {status === "success" && data && (
        <div className={styles.results}>
          <UserCardList users={data.users} />
          <FailedIdList ids={data.failed} />
        </div>
      )}
    </Layout>
  );
}
