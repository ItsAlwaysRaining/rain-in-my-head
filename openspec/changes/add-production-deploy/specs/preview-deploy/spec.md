## MODIFIED Requirements

### Requirement: A preview for every pull request
When a pull request from a branch of this repository is opened or updated, a workflow SHALL build the two-year dataset, build the site, deploy it to Vercel as a **preview** (never production), and post the preview address on the pull request. A later push to the same pull request SHALL update the same comment, not add another.

#### Scenario: Open a pull request
- **WHEN** a pull request is opened from a branch of this repository
- **THEN** within about five minutes the pull request shows a comment with a preview address

#### Scenario: Push again
- **WHEN** another commit is pushed to the same pull request
- **THEN** the existing comment shows the new preview address and the pull request still has one preview comment

#### Scenario: Never production
- **WHEN** the workflow runs for a pull request
- **THEN** the production deployment and the `rain.storyandstructure.studio` address are unchanged, even though the same workflow file also deploys production after a merge

### Requirement: No dataset older than the window
The dataset in a preview SHALL follow the public dataset's window (spec 009): 730 days, ending 7 days before the build. It SHALL contain no play older than that, it SHALL be built fresh for each deploy, and it SHALL NOT be committed. The deploy SHALL stop if the oldest play is more than 738 days old, which is the window and lag (737 days) plus one day of margin, because the oldest play sits at 737.0 days and rounding must not fail a run.

#### Scenario: Check the dataset
- **WHEN** the oldest play in the deployed dataset is queried
- **THEN** it is no more than 738 days older than the deploy date

#### Scenario: A play outside the window
- **WHEN** the built dataset holds a play 739 days old
- **THEN** the run fails before the deploy step

## ADDED Requirements

### Requirement: A preview answers its health check
After deploying a preview, the workflow SHALL ask it for `/api/health` and expect a successful answer saying the app is up, and SHALL ask it for a locked data route with no session and expect a refusal. It SHALL retry for up to two minutes. A preview that fails either check SHALL turn the pull request's deploy check red. The workflow SHALL pass the preview's login without a stored bypass secret and SHALL print only status codes.

#### Scenario: A healthy preview
- **WHEN** the preview answers health and refuses the locked route
- **THEN** the deploy check on the pull request is green

#### Scenario: A broken preview
- **WHEN** the preview does not answer health within two minutes
- **THEN** the deploy check on the pull request is red and names the failed check
