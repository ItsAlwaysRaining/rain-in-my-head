# dashboard-shell Specification

## Purpose
What both dashboards share outside their pages, such as the browser-tab icon, so the Streamlit and TypeScript apps read as one product.

## Requirements

### Requirement: Cloud icon in the browser tab
Both dashboards SHALL show the same cloud icon as the browser tab's icon (favicon) on every page. The icon SHALL come from one shared file, so the two apps can't drift apart. Its colours SHALL be taken from the project palette.

#### Scenario: Streamlit dashboard
- **WHEN** any page of the Streamlit dashboard is open
- **THEN** the browser tab shows the cloud icon

#### Scenario: TypeScript dashboard
- **WHEN** any page of the TypeScript dashboard is open, served by `rain-in-my-head serve` or by the dev server
- **THEN** the browser tab shows the same cloud icon

#### Scenario: One source
- **WHEN** the shared icon file is changed
- **THEN** both dashboards show the changed icon after a restart or rebuild, with no other file edited

### Requirement: Icon legible on light and dark tab bars
The icon SHALL stay recognisable as a cloud at 16×16 px on both a light and a dark browser tab bar. Against white and against the dark tab colour `#202124`, the cloud's silhouette SHALL keep at least 3:1 contrast with the tab: through its outline on one, through its fill on the other.

#### Scenario: Light browser theme
- **WHEN** the dashboard is open in a browser using a light theme
- **THEN** the cloud's outline is clearly visible against the light tab bar at 16px

#### Scenario: Dark browser theme
- **WHEN** the dashboard is open in a browser using a dark theme
- **THEN** the cloud's fill is clearly visible against the dark tab bar at 16px
