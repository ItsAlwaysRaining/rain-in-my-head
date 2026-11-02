# Feature Specification: Usage tracking and a fair-use limit

**Feature Branch**: `feature/usage-tracking`

**Created**: 2026-11-01

**Status**: Draft

**Input**: Hosting phase 5. The hosted site records which invited person opened which pages and used which features, and for how long. The records live in the Neon visitor database from phase 4. The owner reads them on their Mac only (a Visitors page and a command). The site also limits how much of the heavy work (pre-defined queries, genre song lists) one person can ask for, so one visitor can't use up the free hosting limits. Older records are deleted after 12 months, and a nightly copy goes to a private `analytics` branch.

Decided with the owner earlier (hosting plan, 2026-10-27 to 2026-10-29): raw IP addresses are never stored; events older than 12 months are deleted; the nightly export goes to a private `analytics` branch and never to `main`; there are no owner controls on the hosted site, so reporting runs on the owner's Mac only; every hosted page needs a code; the per-person limit on heavy routes belongs in this phase, next to the free-plan usage view.

Out of scope: Vercel preview deploys (phase 6), the production deploy and sending codes to people (phase 7), any tracking on the owner's Mac, and exact CPU use per person (Vercel reports only a total).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The site notices what each person does (Priority: P1)

When an invited person uses the hosted site, it quietly records which pages they open, which features they use (a pre-defined query run by name, a genre's song list) and roughly how long they stay on each page. Nothing changes for the visitor. If recording ever fails, the page still works.

**Why this priority**: every other story in this phase reads or limits what this story records.

**Independent Test**: in a real browser on the hosted build, log in as a guest, open three pages and leave one open for a minute. Then read the stored records directly.

**Acceptance Scenarios**:

1. **Given** a logged-in visitor, **When** they open a page, **Then** one page-view record is stored with their person, the page and the time.
2. **Given** a logged-in visitor, **When** they run a pre-defined query or open a genre's song list, **Then** a feature record is stored with the feature's name and, for a query, which query. What they typed into filters or search boxes is not stored.
3. **Given** a visitor leaves a page open, **When** they move to another page or close the tab, **Then** the time they spent on that page is stored. Time counts only while the page is on screen and the visitor is active, and one visit is capped at 30 minutes.
4. **Given** a visitor who isn't logged in, **When** they open the landing page or the login page, **Then** nothing about them is stored.
5. **Given** the visitor database is slow or unreachable, **When** a visitor uses a page, **Then** the page still works and the missing record is simply lost. A recording failure never blocks the visitor.
6. **Given** a request the site refuses (not logged in, a locked page, a rate-limited request), **Then** it isn't recorded as a page view or a feature use.

---

### User Story 2 - The owner sees who used what, and how much of the free plan is left (Priority: P1)

On my Mac I open a Visitors page, or run one command, and see everyone I've invited: when they last logged in, which pages and features they used, how much time they spent, and how often they hit the limit. I can pick prod or dev. A separate section shows how much of the free hosting limits the site has used this month, so I can see trouble coming before the site pauses.

**Why this priority**: recording is no use if the owner can't read it, and the free-plan view is the early warning the owner asked for.

**Independent Test**: record a few visits as two different people on dev, then open the Visitors page and run the command on the Mac and compare both against a direct query of the stored records.

**Acceptance Scenarios**:

1. **Given** recorded activity, **When** I open the Visitors page on my Mac, **Then** I see each person with their last login, number of visits, time on site, their most used pages, and the features they used.
2. **Given** the same data, **When** I run the usage command, **Then** it shows the same numbers as the page.
3. **Given** I choose a person, **When** I open their detail, **Then** I see their recent activity in time order, with no IP address anywhere.
4. **Given** a date range, **When** I change it, **Then** every number follows it. The choices are the last 7 days, 30 days and 12 months.
5. **Given** the free-plan section, **When** I look at it, **Then** it shows this month's requests and time on heavy pages against the free limits that the site can measure for itself, and the size of the visitor database against its limit. It says plainly that the hosting provider's total processing time is shown only on its own dashboard.
6. **Given** any hosted page or API route, **When** anyone (a guest, a trusted visitor, or someone with no code) asks for the Visitors page or its data, **Then** it's refused. The Visitors page exists only when the app runs on my Mac.
7. **Given** I run the page on my Mac with no visitor database set up, **Then** it says what is missing instead of showing an error.

---

### User Story 3 - One person can't use up the free limits (Priority: P2)

If one visitor asks for a lot of heavy work in a short time (for example by running queries or opening song lists over and over, or with a script), the site slows them down and says why. Everyone else carries on as normal. The owner sees who hit the limit.

**Why this priority**: the hosting plan's tightest limit is processing time. Going over it pauses the whole site until next month. The invite codes are the only lock, so a code that falls into the wrong hands could cause that.

**Independent Test**: in a real browser, as one guest, trigger heavy requests quickly until the limit message appears, then check a second person is unaffected and that the first person recovers after the wait.

**Acceptance Scenarios**:

1. **Given** a visitor sends more than 30 heavy requests within a minute, **When** they send another, **Then** it's refused with a plain message that says they're going too fast and how many seconds to wait. No query runs.
2. **Given** a visitor sends more than 1,000 heavy requests in a day, **When** they send another, **Then** it's refused with a message that says they've reached today's limit and when it resets.
3. **Given** one person is at the limit, **When** another person uses the site, **Then** the second person is unaffected.
4. **Given** a person was limited, **When** the wait is over, **Then** they can carry on without logging in again.
5. **Given** the limit message in the browser, **Then** the visitor sees it as an ordinary notice on the page they're on, not a blank screen or a technical error.
6. **Given** a person hits the limit, **Then** the Visitors page shows that, with the person's name, how often, and when. Many refusals in one minute count as one hit.
7. **Given** a visitor opens ordinary pages and light routes at a normal pace, **Then** they never see the limit.
8. **Given** the limit, **When** I inspect everything the site stored for it, **Then** it's counted per person, with no IP address.

---

### User Story 4 - Visitors know what's tracked, and old records go away (Priority: P2)

The login page tells people what the site records about them: which pages they open, which features they use, and how long they stay. Records are deleted after 12 months. Raw IP addresses are never stored. Visitor records live apart from the listening data, so nobody can reach them through the Analyst page.

**Why this priority**: it's the owner's promise to the people they invite (constitution principle VII), and tracking can't go live without it.

**Independent Test**: read the login page; search every stored record for an IP address; add a record dated 13 months ago and run the nightly clean-up; try to reach visitor records through the SQL page.

**Acceptance Scenarios**:

1. **Given** the login page, **When** I read it, **Then** it says plainly that pages, features and time on site are recorded against my name, how long they're kept (12 months), and that no IP address is stored.
2. **Given** a stored record older than 12 months, **When** the nightly clean-up runs, **Then** it's deleted. A record 11 months old stays.
3. **Given** everything the site stores, **When** I search it for an IP address in any common form, **Then** none is found.
4. **Given** a trusted visitor on the Analyst page, **When** they try to reach visitor, session or usage records, **Then** they can't. Those records aren't in the data the page can query.
5. **Given** a revoked person, **Then** their past records stay until they age out, so the owner's history stays accurate. The person can no longer log in.

---

### User Story 5 - A nightly copy lands on a private branch (Priority: P3)

Each night the visitor records are copied to a private `analytics` branch in the repository, so the owner has a backup that doesn't depend on the free database. The copy never touches `main`.

**Why this priority**: it protects against losing the free database, but the site works without it.

**Independent Test**: run the export by hand on dev, then check the `analytics` branch has the file and `main` doesn't.

**Acceptance Scenarios**:

1. **Given** recorded activity, **When** the nightly export runs, **Then** the `analytics` branch holds a copy of the usage records and the list of people, without any invite code or code hash.
2. **Given** the export, **Then** `main` and every feature branch are unchanged by it, and no visitor data appears in any pull request.
3. **Given** a night with no new activity, **When** the export runs, **Then** it makes no new commit.
4. **Given** the export fails, **Then** the owner can see that it failed from the workflow's own status. The site isn't affected.
5. **Given** the export has run on many nights, **When** I look at the `analytics` branch, **Then** it holds only the latest copy, with no earlier copies in its history. A record deleted from the database after 12 months is therefore gone from the branch by the next night's export (decided with the owner, 2026-11-01).

### Edge Cases

- **A visitor with two tabs open.** Each tab's time is recorded separately and the page-view count is per page opened. Time on site counts the longer of any overlap once.
- **A visitor who leaves a page open all night.** One visit is capped at 30 minutes, and time stops counting when the page is hidden or the visitor is idle.
- **A visitor who clicks back and forth quickly.** Every page opened is a page view, but a reload within 5 seconds of the same page isn't counted twice.
- **A session that ends mid-visit** (revoked, expired or logged out). The time spent up to that moment is stored if possible, and nothing more is recorded after it.
- **A revoked person's name is reused.** Their old records stay under the old person. The new code starts a new history.
- **Recording and the limit use the visitor database.** If it's unreachable, recording is skipped (Story 1, scenario 5). The limit check can't be made, so heavy requests are refused with the same plain "try again in a minute" message the locked pages already give, rather than let through unchecked.
- **A visitor who changes tier or gets a page granted.** Their old records are unchanged. New activity is recorded as usual.
- **A heavy request that is refused for another reason** (the SQL route for a guest). The 403 comes first and it doesn't count towards the limit.
- **A request from a script that sends a valid session.** It's limited by person exactly like a browser, because the limit is per person, not per device.
- **A person with a very long name or a name with unusual characters.** The Visitors page shows it as text and never runs it as anything else.
- **The owner's own Mac.** No login, nothing recorded, no limit. The Visitors page there only reads the hosted records.
- **The first check after the database has been idle.** It can take about a second. That's acceptable; recording never delays a page.
- **Time zones.** The "day" for the daily limit and the monthly figures runs on UTC, and the Visitors page says so.
- **A route added later that is heavy but isn't on the list.** It isn't limited until it's added, and the plan lists how to add one. Routes still deny by default (constitution VII).

## Requirements *(mandatory)*

### Functional Requirements

**Recording**

- **FR-001**: On the hosted site, the system MUST record a page view for each page a logged-in visitor opens, storing the person, the page and the time.
- **FR-002**: The system MUST record a feature use for each pre-defined query run and each genre song list opened, storing the person, the feature, the query's name where there is one, and the time. It MUST NOT store anything a visitor typed or chose in filters or search boxes.
- **FR-003**: The system MUST record the time a visitor spends on each page, counting only while the page is on screen and the visitor is active, capped at 30 minutes per visit.
- **FR-004**: The system MUST NOT record anything for someone who isn't logged in, and MUST NOT record requests that were refused.
- **FR-005**: A failure to record MUST NOT block, slow or change what the visitor sees.
- **FR-006**: The system MUST NOT store a raw IP address, a code, or a code hash in any usage record, and MUST NOT put one in a log (constitution VII).
- **FR-007**: When the app runs on the owner's Mac (not hosted), the system MUST record nothing and apply no limit, and everything MUST work as before.

**Fair-use limit**

- **FR-008**: The system MUST limit each person's heavy requests. The heavy routes are the pre-defined query route and the genre song list route. The first limits are 30 requests in a minute and 1,000 in a day.
- **FR-009**: A limited request MUST be refused before any work is done, with a plain message that says the visitor is going too fast and how long to wait (or that today's limit is reached and when it resets).
- **FR-010**: The limit MUST be counted per person and MUST NOT use or store an IP address. One person's limit MUST NOT affect another's.
- **FR-011**: A request refused for another reason (not logged in, not allowed) MUST NOT count towards the limit. A limited request MUST NOT count towards a later limit.
- **FR-012**: The system MUST record each time a person hits the limit (one record per person per minute at most), so the owner can see it.
- **FR-013**: When the limit can't be checked because the visitor database is unreachable, heavy requests MUST be refused with a "try again in a minute" message instead of being let through.
- **FR-014**: The limits MUST be changeable in one place without changing how they work, and the owner MUST be able to review them in this spec.

**Owner reporting (Mac only)**

- **FR-015**: The system MUST provide a Visitors page and a usage command, both running only on the owner's Mac, that read the hosted visitor database. Both MUST show the same numbers. They MUST take a choice of prod or dev, like the `viewer` commands, and make clear which one they are using.
- **FR-016**: For each person, the report MUST show their last login, number of visits, total time on site, their most used pages and features, and how often they hit the limit. For a chosen range (last 7 days, 30 days or 12 months).
- **FR-017**: The report MUST show a person's recent activity in time order.
- **FR-018**: The report MUST include a free-plan section: this month's request count and time on heavy pages from the site's own records, the visitor database's size against its limit, and a plain note that the hosting provider's processing time is shown only on its dashboard. It MUST NOT promise exact processing time per person.
- **FR-019**: The Visitors page and its data MUST NOT be reachable on the hosted site by anyone. No tier opens it, and a grant MUST NOT be able to open it.

**Privacy and retention**

- **FR-020**: The login page MUST say what is recorded (pages, features, time on site, against the person's name), how long records are kept (12 months), and that no IP address is stored. This extends the notice from phase 4.
- **FR-021**: Usage records older than 12 months MUST be deleted automatically each day. The clean-up MUST NOT delete newer records, people, or sessions.
- **FR-022**: Usage records MUST live in the visitor database, separate from the listening data, so the Analyst page can't reach them (constitution VII).
- **FR-023**: The records of a revoked person MUST stay until they age out.

**Nightly export**

- **FR-024**: The system MUST copy the usage records and the list of people (names, tiers and dates only) to the private `analytics` branch every night. It MUST NOT include any code, code hash, session or IP address.
- **FR-025**: The export MUST NOT write to `main` or any branch other than `analytics`, and MUST NOT appear in a pull request. A night whose copy is identical to the last one MUST NOT produce a new commit.
- **FR-026**: A failed export MUST show as a failed workflow run and MUST NOT affect the site.
- **FR-027**: The `analytics` branch MUST hold only the latest copy: when the copy changes, the branch is replaced by one fresh commit, so earlier copies leave its history and the 12-month promise holds there too. This replacement applies to the `analytics` branch only.

**Cost and environments**

- **FR-028**: Everything in this phase MUST fit the free plans with no card (constitution VII). It MUST NOT add a paid service or a new account.
- **FR-029**: Dev and prod MUST use separate usage records. A record from one MUST NOT appear in the other.

- **FR-030**: Because the browser reports page views and time on page, a person MUST NOT be able to flood the site with those reports. Each person is capped at 120 reports a minute. Reports over the cap are dropped without an error, and the visitor sees nothing. Added during planning (2026-11-01), when the plan found that this path costs processing time like a heavy route.

### Key Entities

- **Usage record**: one thing a person did: a page view, a feature use, a time-on-page measurement, or a limit hit. Has the person, the page or feature, the time, and where it applies the length of time or the query's name. Kept 12 months.
- **Person**: from phase 4. Usage is tied to them by their name's record, and nothing more.
- **Heavy route**: a route that costs the free plan real processing time (the pre-defined query route and the genre song list route). Limited per person.
- **Limit counter**: how many heavy requests one person has sent in the last minute and the last day. Kept per person, with no IP address, and discarded when its window passes.
- **Visitors report**: the owner's view of all of the above, on the Mac only.
- **Free-plan figures**: the numbers the site can measure for itself (requests, time on heavy pages, database size), shown against the free limits.
- **Analytics copy**: the nightly export on the private `analytics` branch.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: After a guest opens 3 pages and runs 2 queries in a real browser, the owner's report shows exactly 3 page views and 2 feature uses for that person within 1 minute, and the same numbers match a direct query of the stored records.
- **SC-002**: A person who sends 31 heavy requests within a minute gets 30 answers and 1 refusal with the "going too fast" message. A second person at the same moment gets 100% normal answers.
- **SC-003**: After the wait stated in the message, the limited person can use the site again without logging in.
- **SC-004**: With the visitor database switched off, 100% of page loads still work for a logged-in visitor, and 100% of heavy requests are refused with a "try again" message.
- **SC-005**: A search of everything stored by this phase, including the nightly export, finds no IP address, no code and no code hash.
- **SC-006**: A record dated 13 months ago is gone after the nightly clean-up, and a record dated 11 months ago is still there.
- **SC-007**: 100% of hosted requests for the Visitors page or its data are refused, for guest, trusted and no-code visitors, and for a visitor granted every other page.
- **SC-008**: The Visitors page and the usage command show identical figures for the same range.
- **SC-009**: Running the app on the Mac behaves exactly as before: the existing checks pass, nothing is recorded and no limit applies.
- **SC-010**: A run of the nightly export leaves `main` unchanged and adds the copy to `analytics`.
- **SC-011**: The hosting and database plans stay free with no card, and the Visitors page shows the database size against its free limit.

## Assumptions

- The visitor database is the Neon project from phase 3, with separate dev and prod branches. The prod tables and the site's database role were created on 2026-11-01 (`viewer init --env prod`). This phase adds more tables there, and `viewer init` stays safe to run twice.
- The site's servers remember nothing between requests, so the limit counters live in the visitor database. This is why the limit adds a small cost to each heavy request, which is acceptable.
- The owner reads usage on their Mac through the existing owner connection (the same one the `viewer` commands use). The hosted site's own database role can add usage records and read back the few columns it needs to count them for the limit. It can't change or delete a usage record, or change anything about people (as in phase 4). It already reads people, including code hashes, so this adds no new kind of exposure.
- "Heavy routes" start as the pre-defined query route and the genre song list route, because those cost the most processing time. Other routes cost little and aren't limited.
- The starting limits (30 a minute, 1,000 a day) are the owner's to review. A normal visitor clicking around never gets near them.
- A "day" and a "month" run on UTC.
- Time on a page comes from the visitor's browser reporting it when they leave the page. It's an estimate, not an exact measure, and the report says so.
- The login page notice starts from phase 4's wording and adds the new items.
- The nightly export runs from a scheduled GitHub workflow using a secret that already exists or is made by OpenTofu, and no new accounts. Which secret is for the plan.
- Replacing the `analytics` branch each night is a force-update, which `CLAUDE.md` and the constitution rule out for code branches. The plan treats this as a narrow exception: only the scheduled workflow does it, only to `analytics`, and it's recorded in the plan's Complexity Tracking. Nobody, and no Claude session, force-pushes `main` or a feature branch.
- The Visitors page is part of the TypeScript dashboard only, and appears only when the app runs on the Mac. Streamlit gets no Visitors page, and the difference is noted in `docs/streamlit-vs-typescript.md`.
- Sending codes to people, and the first look at real visitors' data, belong to phase 7.
