# Roadmap

## Phase 0: Report Hygiene

Status: immediate operational change.

- Export PDFs natively instead of printing to PDF.
- Update or remove the expired certification badge.
- Adopt the improved report structure from the Administrative Building mockup.
- Add findings tables, captions, page numbers, and thermal palette explanation to manual reports.

## Phase 1: MVP Report Generator

Goal: Generate the improved report from structured inspection data.

Deliverables:

- `inspection.yaml` schema.
- Word/docx template with placeholders.
- CLI command to generate `.docx`.
- Optional searchable PDF export.
- Validation for missing required fields and missing image assets.
- Sample Administrative Building inspection fixture.

Success criteria:

- Nate can generate a complete editable report from one inspection folder.
- The report includes cover metrics, inspection details, findings table, overview pages, anomaly detail pages, and recommendations.
- Total anomalous area and anomaly count are computed from data.
- Searchable PDF output is available.
- A large report with 25-40 anomalies remains navigable.

## Phase 2: Annotation UI

Goal: Capture structured data during image annotation.

Deliverables:

- Local web app for loading high-resolution thermal/visual images.
- Pan/zoom drawing tools for boxes or polygons.
- Auto-assigned anomaly IDs.
- Per-anomaly form for location, severity, observation, and recommendation.
- Approximate area calculation from geometry and scale.
- Rendered annotated overview image.
- Auto-generated close-up crops.
- Generate report button using the Phase 1 renderer.

## Phase 3: Projects, Rollups, and History

Goal: Turn one-off reports into a repeatable inspection product.

Deliverables:

- Client, property, inspection, image, and anomaly entities.
- Engagement-level rollup reports.
- Standard boilerplate libraries for equipment, technicians, and recommendation text.
- Re-scan comparison for new, grown, reduced, and resolved anomalies.
