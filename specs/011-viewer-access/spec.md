# Feature Specification: Invite codes and locked pages

**Feature Branch**: `feature/viewer-access`

**Created**: 2026-10-29

**Status**: Draft

**Input**: Hosting phase 4. The hosted site gets a front door. The owner creates one invite code per person from their Mac (`viewer add`, `list`, `revoke`, `grant`). A visitor enters the code on a login page and gets a signed cookie. Every page and API route is denied by default and opens only if that person's access allows it. Only the landing page and the login page are public. Each person is a guest or a trusted visitor, and the owner can grant individual pages on top. The navigation hides pages a visitor can't open. Revoking a code logs that person out straight away. Codes are stored only as hashes. Viewer and session records live in the Neon database created in phase 3.

Decided with the owner earlier (hosting plan, 2026-10-27 and 2026-10-28): every page needs a code; visitors get pre-defined queries only and no AI on the SQL page; there are no owner controls on the hosted site, so the viewer commands and the Visitors page run on the owner's Mac only; raw IP addresses are never stored.

Out of scope: usage tracking and the Visitors page (phase 5), Vercel preview deploys (phase 6), production deploy and sending codes to people (phase 7).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The owner invites someone (Priority: P1)

From my Mac I run one command with a person's name. It gives me a code for that person, shown once. I send it to them myself. I can list everyone I've invited, see whether each code is active or revoked, and see which pages each person can open.

**Why this priority**: without a way to create codes, nobody can get in, and nothing else in this phase can be tried.

**Independent Test**:
1. Run `viewer add` with a name.
2. Run `viewer list`.
3. Search the visitor database for the code you were shown.

**Acceptance Scenarios**:

1. **Given** no one has been invited, **When** I run `viewer add` with a name, **Then** I see a new code once, and the person appears in `viewer list` as a guest with an active code.
2. **Given** I add a person as trusted, **When** I run `viewer list`, **Then** they're listed as trusted.
3. **Given** I've been shown a code, **When** I search everything stored in the visitor database for it, **Then** it isn't there. Only a one-way scramble of it is.
4. **Given** I've lost a person's code, **When** I look for a way to see it again, **Then** there isn't one. I revoke the old code and add the person again.
5. **Given** a name that already has an active code, **When** I run `viewer add` with it, **Then** I'm told so and nothing changes.
6. **Given** the hosted site, **When** anyone looks for a way to add, list, revoke or grant, **Then** there isn't one. These commands exist only on my Mac.

---

### User Story 2 - A visitor logs in and sees only their pages (Priority: P1)

I get a code from the owner. I open the site, enter it on the login page, and land on the pages I'm allowed to see. The navigation shows only those pages. If I type the address of a page I'm not allowed to open, I'm told it isn't available to me. Without a code I can see the landing page and the login page, and nothing else.

**Why this priority**: this is the front door. The site can't go online without it.

**Independent Test**: in a real browser on the hosted build, with a guest code, go through every page and every API route, with and without a code.

**Acceptance Scenarios**:

1. **Given** I have no code, **When** I open any page other than the landing page or the login page, **Then** I'm sent to the login page.
2. **Given** I have no code, **When** I call any API route directly, **Then** it's refused with a 403 and nothing is returned.
3. **Given** a valid guest code, **When** I enter it on the login page, **Then** I'm logged in and taken to the dashboards.
4. **Given** I'm logged in as a guest, **When** I open Genre, **Then** it loads with data.
5. **Given** I'm logged in as a guest, **When** I request the SQL route, **Then** I get a 403 and no query runs.
6. **Given** I'm logged in as a guest, **When** I look at the navigation, **Then** the Analyst link isn't there.
7. **Given** I'm logged in as a guest, **When** I type the Analyst address into the browser, **Then** I see a plain "not available to you" page, not a blank screen or an error.
8. **Given** I'm logged in as trusted, **When** I open the Analyst page, **Then** I can pick a pre-defined query and see its results. I still can't type my own.
9. **Given** I enter a wrong code, **Then** I'm told the code didn't work, with no hint about whether it was close or whether the person exists.
10. **Given** I'm logged in, **When** I press Log out, **Then** my session ends and the next page I open sends me to the login page.
11. **Given** I'm logged in, **When** I look at the site's cookies, **Then** the login cookie can't be read by page scripts and is only sent over a secure connection.

---

### User Story 3 - The owner revokes or changes someone's access (Priority: P2)

When I stop trusting a code, I revoke it and that person is logged out straight away, on whatever device they're using. I can also give one person an extra page without making them trusted, or take a page back.

**Why this priority**: invite codes can be passed around. Without revocation, a code that got out can't be undone.

**Independent Test**: log in as a guest in a real browser, then run `viewer revoke` and click again. Repeat with `viewer grant`.

**Acceptance Scenarios**:

1. **Given** a guest is logged in on two browsers, **When** I run `viewer revoke` for them, **Then** the next click in either browser sends them to the login page.
2. **Given** a revoked code, **When** anyone enters it on the login page, **Then** it's refused like any wrong code.
3. **Given** a guest, **When** I run `viewer grant` for the Analyst page, **Then** their next click (or a reload) shows the Analyst link, and they can open it. They stay a guest otherwise.
4. **Given** a granted page, **When** I take the grant back, **Then** their next click shows the page is no longer available.
5. **Given** a guest, **When** I change them to trusted, **Then** they can open every page a trusted visitor can, without logging in again.
6. **Given** a revoked person, **When** I add them again, **Then** they get a new code, and the old code still doesn't work.

---

### User Story 4 - Guessing codes doesn't work (Priority: P3)

If someone tries codes over and over, the site slows them down and then stops them, without storing their IP address.

**Why this priority**: codes are the only lock on the site, so scripted guessing has to be impractical.

**Independent Test**: send repeated wrong codes from one source, then try a correct code from the same source and from another one. Then inspect everything the site stored.

**Acceptance Scenarios**:

1. **Given** one source sends more than 5 wrong codes within a minute, **Then** further attempts in that minute are refused without being checked.
2. **Given** one source has sent 20 wrong codes, **Then** it's locked out for a short period, even if it then sends a correct code.
3. **Given** one source is locked out, **When** another source sends a correct code, **Then** it works.
4. **Given** the guessing above, **When** I inspect everything the site stored, **Then** no raw IP address is in it.

### Edge Cases

- **A visitor with an old cookie after the owner changes the site's signing secret.** They're sent to the login page, not shown an error.
- **A cookie that was edited by hand.** It's treated as no cookie.
- **Two people with the same name.** Names are unique among active codes, so the second `viewer add` is refused (Story 1, scenario 5).
- **A code that's entered with extra spaces or in lower case.** Spaces around it are ignored. The code is case-sensitive, so a wrong-case code fails like any other.
- **A visitor's session outlives their tier change.** The new tier applies on their next request.
- **A route added later that forgets to declare who may use it.** It's refused (constitution VII).
- **The visitor database is unreachable.** No one new can log in and existing sessions can't be checked, so every locked page is refused with a plain "try again in a minute" message. Nothing is shown to anyone who can't be checked.
- **The owner runs the app on their Mac.** There's no login and everything works as before (local mode is unchanged).
- **A request that comes from another website** (for example, a hidden form on a page the visitor opened elsewhere). The login and logout actions refuse it.
- **The API docs.** They aren't served on the hosted site (already true from phase 2) and stay off.
- **A code appearing in a log, a URL or an error message.** It must not. Only the person's name may be logged.

## Requirements *(mandatory)*

### Functional Requirements

**Owner commands**

- **FR-001**: The system MUST provide `viewer add`, `viewer list`, `viewer revoke` and `viewer grant` commands. They MUST run only on the owner's Mac and MUST NOT be reachable from the hosted site.
- **FR-002**: `viewer add` MUST take a name and an optional tier (guest by default, or trusted), create a random code of at least 12 characters, and show it once.
- **FR-003**: The system MUST NOT store a code. It stores only a one-way scramble of it, and there MUST be no way to see a code again.
- **FR-004**: `viewer list` MUST show each person's name, tier, extra pages granted, whether their code is active or revoked, and when it was created.
- **FR-005**: `viewer revoke` MUST make a person's code unusable and end all their sessions.
- **FR-006**: `viewer grant` MUST add a page to, or take a page from, one person's access, and MUST also change a person's tier.
- **FR-007**: The commands MUST work against the dev and prod visitor databases separately, and MUST make clear which one they're using.

**Login and sessions**

- **FR-008**: The login page MUST be public. It MUST accept a code and, if the code is active, start a session for that person.
- **FR-009**: The login page MUST say what the site stores about a visitor at this stage (their name, tied to their code, and when they log in). Phase 5 extends this when usage tracking is added.
- **FR-010**: A wrong, revoked or unknown code MUST get the same plain message, with no hint of whether the person exists.
- **FR-011**: A session MUST be kept in a cookie that page scripts can't read, that is only sent over a secure connection, and that can't be forged or edited. The system MUST also keep a record of each session on its side, so a session can be ended.
- **FR-012**: A session MUST end after 30 days, and on log out. A visible Log out control MUST be available to every logged-in visitor.
- **FR-013**: The login and logout actions MUST refuse requests that don't come from the site's own pages.
- **FR-014**: Repeated wrong codes MUST be limited: more than 5 per minute from one source are refused unchecked, and 20 wrong codes lock that source out for a short period. The system MUST NOT store raw IP addresses to do this.
- **FR-015**: A code MUST NOT appear in any log, URL, error message or stored record.

**Locked pages**

- **FR-016**: On the hosted site, every page and every API route MUST be denied by default. Only the landing page and the login page (and what they need to load) are public.
- **FR-017**: Every API route MUST declare who may use it. A route that declares nothing MUST be refused (constitution VII).
- **FR-018**: Access MUST come from a person's tier plus any pages granted to them. A guest opens the dashboard pages. A trusted visitor opens those and the Analyst page (pre-defined queries and the schema map). No tier opens a page that's off on the hosted site (playlists, AI).
- **FR-019**: A request for a page the visitor can't open MUST get a clear answer: the login page if they aren't logged in, or a plain "not available to you" page if they are. A locked API route MUST get a 403 with a short message.
- **FR-020**: The navigation MUST show only the pages the logged-in visitor can open. Hiding a link is a convenience only. The server MUST check every request.
- **FR-021**: A tier or grant change MUST apply on the person's next request, without a new login.
- **FR-022**: A revoked person's next request MUST be refused as if they had no session.

**Data and local mode**

- **FR-023**: Viewer, session and attempt records MUST live in the visitor database, separate from the listening data, so the SQL page can't reach them (constitution VII).
- **FR-024**: Dev and prod MUST use separate visitor databases. A code made for one MUST NOT work on the other.
- **FR-025**: When the app runs on the owner's Mac (not hosted), there MUST be no login, and every page and route MUST work as before.
- **FR-026**: The visitor-only rules from phase 2 MUST stay in force on top of this: the SQL page runs only pre-defined queries, and AI and playlist routes are refused.

### Key Entities

- **Person**: someone the owner invited. Has a unique name, a tier (guest or trusted), a list of extra pages, a status (active or revoked) and a created date.
- **Invite code**: one per person at a time. Stored only as a one-way scramble. Replaced when a person is added again after a revoke.
- **Tier**: guest or trusted. Decides the starting set of pages. The owner has no hosted tier, because owner actions run on the Mac only.
- **Page access**: a page a person may open, from their tier or from a grant.
- **Session**: one login on one device, for one person, ending after 30 days or when ended by revoke or log out.
- **Login attempt count**: how many wrong codes one source has sent recently, kept without a raw IP address and discarded after the lockout period.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The owner can add a person and have a code ready to send in under 30 seconds.
- **SC-002**: With no code, 100% of pages and API routes other than the landing page and login page are refused (checked against the full list of routes).
- **SC-003**: In a real browser, a guest code opens Genre, and the same guest gets a 403 on the SQL route.
- **SC-004**: After the owner revokes a code, the person's next click is refused within 5 seconds, on every device they were using.
- **SC-005**: A search of everything stored in the visitor database finds no code and no raw IP address.
- **SC-006**: After 20 wrong codes from one source, 100% of further attempts from it are refused for the lockout period, and a correct code from another source still works.
- **SC-007**: For each tier, the pages shown in the navigation match the pages the server will open: 0 links lead to a refusal, and 0 hidden pages open when typed.
- **SC-008**: Running the app locally behaves exactly as before: the existing checks pass with no login.

## Assumptions

- The visitor database is the Neon project created in phase 3, with its dev and prod branches. The app already has the connection and the session-signing secret as hosted settings (set by OpenTofu), so no new accounts or tokens are needed.
- "Guest" opens the dashboard pages (Overview, New artists, Genre, Artist, When you listen, Mainstream vs. niche) plus About and Contact Me. "Trusted" adds the Analyst page and Storm. The owner can change this per person with grants. These starting sets are the owner's to review in this spec.
- A session lasts 30 days, which suits friends who visit now and then. A shorter or longer time is a one-line change.
- The owner sends codes to people themselves. Phase 7 covers that.
- The login page's tracking notice starts with what this phase stores. Phase 5 adds pages, features and time on site when it starts recording them.
- Usage tracking, the Visitors page and any "last seen" column are phase 5. This phase records only that a login happened, not what the person does.
- The Neon database sleeps when idle and the first check after a quiet spell can take about a second. That's acceptable for a login.
- Streamlit and the playlist and AI features stay local, as decided in the hosting plan.
