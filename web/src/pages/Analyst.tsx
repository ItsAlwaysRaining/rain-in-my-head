// Analyst: the SQL and Schema pages on one page, as in the Figma prototype. The schema map sits in a
// collapsible card above the editor (open when arriving from the old /schema address).
import { useSearchParams } from "react-router";
import { PageHeader } from "../components/ui";
import styles from "./Analyst.module.css";
import Schema from "./Schema";
import Sql from "./Sql";

export default function Analyst() {
  const [params] = useSearchParams();
  return (
    <>
      <PageHeader title="Analyst">Explore your listening with SQL. Queries are read-only, so they can't change your data.</PageHeader>
      <details className={styles.schema} open={params.get("schema") === "open"}>
        <summary>Database schema</summary>
        <div className={styles.schemaBody}>
          <Schema />
        </div>
      </details>
      <div className={styles.sql}>
        <Sql />
      </div>
    </>
  );
}
