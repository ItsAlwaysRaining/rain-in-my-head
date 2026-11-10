# Spec Delta

## Purpose

The Mainstream vs. niche page lists the artists in one Last.fm listener band, so a reader can see which artists make up each bar of the Overview's mainstream chart and find the niche artists they play.

## ADDED Requirements

### Requirement: The page shows one listener band
The Mainstream vs. niche page SHALL show the band's name, its share of the user's plays in the range, and the range it covers. The band is one of the five labels the Overview chart uses (`<10k`, `10k–100k`, `100k–1M`, `1M–5M`, `5M+`). The share is calculated the same way as the chart's bar, so it matches the bar exactly.

#### Scenario: Band with plays
- **WHEN** the user opens the page for the band `100k–1M` for the last 12 months, and that band holds 18% of the plays with a known listener count
- **THEN** the page shows the band name `100k–1M`, the share `18%`, and the last 12 months as the range

#### Scenario: Unknown band
- **WHEN** the page is opened with a band that is not one of the five labels
- **THEN** the page shows a notice that the band does not exist and no artist table

### Requirement: The page lists the artists in the band
The page SHALL list the 100 most played artists in the band with at least one play in the range. When the band has more than 100 such artists, the page SHALL say how many it has in total. Each row SHALL show the artist's name, the artist's Last.fm listener count, and the user's play count for that artist in the range. Rows SHALL be sorted by play count, highest first. An artist belongs to the band its Last.fm listener count falls in, using the same thresholds as the chart. An artist whose listener count is unknown is not listed.

#### Scenario: Artists sorted by plays
- **WHEN** the band `10k–100k` has artists Geese (42 plays) and Big Thief (57 plays) in the range
- **THEN** the table lists Big Thief first, then Geese, each with its listener count and play count

#### Scenario: More than 100 artists
- **WHEN** the band `10k–100k` has 10,000 artists with plays in the range
- **THEN** the table lists the 100 most played, and the page says "Showing the top 100 of 10,000 artists"

#### Scenario: Plays add up to the bar
- **WHEN** the page for a band is opened
- **THEN** the sum of the plays in its table equals the band's share of the known-listener plays in the range

#### Scenario: Band with no artists in the range
- **WHEN** no artist in the band has a play in the range
- **THEN** the page shows a notice that no artists are in this band for this range, and no empty table

### Requirement: The page follows the Overview's range
The page SHALL use the range carried in its address (`start` and `end`). When the Overview has a selected period, the link carries that period's dates, so the page covers the same plays as the bar that was clicked.

#### Scenario: Opened from a selected period
- **WHEN** March 2026 is selected on the Overview and the user clicks the `1M–5M` bar
- **THEN** the page covers 1–31 March 2026 only

### Requirement: The page links back to the Overview
The page SHALL show a "Back to Dashboards" link that opens the Overview.

#### Scenario: Back link
- **WHEN** the user clicks "Back to Dashboards" on the page
- **THEN** the Overview opens

### Requirement: Mainstream page is available to guests
The Mainstream vs. niche page and its data SHALL be open to every visitor who can open the Dashboards pages, under the existing `mainstream` page key.

#### Scenario: Guest opens the page
- **WHEN** a guest who can open the Dashboards pages opens the Mainstream vs. niche page
- **THEN** the page loads its data and shows the artist table
