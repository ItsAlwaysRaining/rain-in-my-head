// Shown when someone who is logged in opens a page their code doesn't allow (specs/011-viewer-access).
import { Link } from "react-router";
import { Notice, PageHeader } from "../components/ui";

export default function NotAvailable() {
  return (
    <>
      <PageHeader title="Not available to you">That page isn't available to you.</PageHeader>
      <Notice>
        Your invite code doesn't include it. Go back to <Link to="/dashboards">Dashboards</Link>, or ask the person who invited you.
      </Notice>
    </>
  );
}
