## ADDED Requirements

### Requirement: Playlist Generator opens for every tier
On the hosted site, a logged-in guest and a trusted visitor SHALL both be able to open Playlist Generator. On the owner's Mac it opens as it does today.

#### Scenario: Guest opens it
- **WHEN** a logged-in guest opens Playlist Generator
- **THEN** the form and its track preview load

#### Scenario: Logged out
- **WHEN** a visitor who is not logged in opens Playlist Generator
- **THEN** they are sent to the login page

### Requirement: Read-only playlist routes work on the hosted site
The hosted API SHALL answer `GET /api/playlists/meta` and `POST /api/playlists/preview` for a logged-in visitor whose pages include `playlists`. Both only read the two-year `public.db`. A person without the `playlists` page SHALL be refused, as with every other data route.

#### Scenario: Preview answers
- **WHEN** a logged-in guest requests a playlist preview
- **THEN** the API answers 200 with the preview's title, columns and rows

#### Scenario: Not logged in
- **WHEN** a request without a login calls either route
- **THEN** the API answers 403 `login_required`

### Requirement: Creating a playlist is refused on the hosted site
On the hosted site every other `/api/playlists*` route SHALL stay refused with 403 `refused` and the message "This DJ doesn't take requests.", for everyone including trusted visitors. This includes `POST /api/playlists/create` and `GET /api/playlists/spotify`, and any playlist route added later. No Spotify credential is used or needed.

#### Scenario: Create is refused
- **WHEN** a trusted visitor calls `POST /api/playlists/create`
- **THEN** the API answers 403 `{"error": "refused", "message": "This DJ doesn't take requests."}` and nothing is written

#### Scenario: A new route stays closed
- **WHEN** a route is later added under `/api/playlists/` and not listed as read-only
- **THEN** the hosted site refuses it

### Requirement: The hosted form says why Create is off
On the hosted site, the page SHALL show the **Create on Spotify** button. Clicking it SHALL show "This DJ doesn't take requests." in a friendly notice, not the red error style. The page SHALL NOT show the "Connect Spotify from the terminal" instructions on the hosted site. On the owner's Mac, Create on Spotify SHALL work as it does today.

#### Scenario: Guest clicks Create
- **WHEN** a guest clicks Create on Spotify
- **THEN** a notice reads "This DJ doesn't take requests." and no playlist is created

#### Scenario: Owner on their Mac
- **WHEN** the owner clicks Create on Spotify on their Mac with Spotify connected
- **THEN** the playlist is created as before
