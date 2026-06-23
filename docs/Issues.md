# TrueVector GitHub Issues

Registered snapshot of open GitHub Issues from [davidklan-png/TrueVector](https://github.com/davidklan-png/TrueVector/issues).

- Snapshot date: 2026-06-23
- Source: GitHub Issues (all opened 2026-06-22)
- Open issues: 12

| # | Title | Milestone | Labels |
|---|-------|-----------|--------|
| 1 | [Stop using print-to-PDF and document the export workflow](#1-stop-using-print-to-pdf-and-document-the-export-workflow) | Phase 0: Report hygiene | docs, phase-0, template |
| 2 | [Update or remove expired certification badge from report materials](#2-update-or-remove-expired-certification-badge-from-report-materials) | Phase 0: Report hygiene | phase-0, question, template |
| 3 | [Finalize the MVP DOCX report template](#3-finalize-the-mvp-docx-report-template) | Phase 1: MVP report generator | mvp, phase-1, template |
| 4 | [Define and validate the inspection.yaml schema](#4-define-and-validate-the-inspectionyaml-schema) | Phase 1: MVP report generator | engineering, mvp, phase-1 |
| 5 | [Build local web app and report generator](#5-build-local-web-app-and-report-generator) | Phase 1: MVP report generator | engineering, mvp, phase-1 |
| 6 | [Add searchable PDF export and text-layer verification](#6-add-searchable-pdf-export-and-text-layer-verification) | Phase 1: MVP report generator | engineering, mvp, phase-1 |
| 7 | [Create complete Administrative Building sample fixture](#7-create-complete-administrative-building-sample-fixture) | Phase 1: MVP report generator | docs, mvp, phase-1, template |
| 8 | [Prove the MVP workflow on a large 25+ anomaly report](#8-prove-the-mvp-workflow-on-a-large-25-anomaly-report) | Phase 1: MVP report generator | engineering, mvp, phase-1, product |
| 9 | [Invite Nate to the repository once his GitHub username is confirmed](#9-invite-nate-to-the-repository-once-his-github-username-is-confirmed) | Phase 0: Report hygiene | product, question |
| 10 | [Set up Python web server and inspection data persistence](#10-set-up-python-web-server-and-inspection-data-persistence) | Phase 1: MVP report generator | engineering, mvp, phase-1 |
| 11 | [Build thermal image markup UI](#11-build-thermal-image-markup-ui) | Phase 1: MVP report generator | engineering, mvp, phase-1 |
| 12 | [Build orthomosaic anomaly ID placement UI](#12-build-orthomosaic-anomaly-id-placement-ui) | Phase 1: MVP report generator | engineering, mvp, phase-1 |

---

## #1 Stop using print-to-PDF and document the export workflow

- State: Open
- Milestone: Phase 0: Report hygiene
- Labels: docs, phase-0, template
- Link: https://github.com/davidklan-png/TrueVector/issues/1

### Goal

Future reports should use native PDF export so the PDF has searchable/selectable text and can be indexed by client document systems.

### Acceptance criteria

- The workflow is documented in `docs/product/`.
- Manual report process says to use File -> Download -> PDF or equivalent native export.
- Existing Hazel Park PDFs are re-exported if the source Google Docs are still available.

### Context

The review found that print-driver PDFs had broken text layers, which is a critical accessibility and indexing defect.

---

## #2 Update or remove expired certification badge from report materials

- State: Open
- Milestone: Phase 0: Report hygiene
- Labels: phase-0, question, template
- Link: https://github.com/davidklan-png/TrueVector/issues/2

### Goal

No future report should display a stale or expired certification badge.

### Acceptance criteria

- Confirm whether the ITC Level II certification was renewed.
- If renewed, update the badge and source template with the current expiration.
- If not renewed, remove the badge and adjust credentials language.
- Add a validation rule to the MVP spec or schema for certification expiration versus inspection date.

### Context

The report feedback found an ITC badge with an expiration date of May 7, 2025 on reports dated June 8, 2026.

---

## #3 Finalize the MVP DOCX report template

- State: Open
- Milestone: Phase 1: MVP report generator
- Labels: mvp, phase-1, template
- Link: https://github.com/davidklan-png/TrueVector/issues/3

### Goal

Create the template the report generator will fill, based on the Administrative Building mockup.

### Acceptance criteria

- Template includes cover, table of contents, inspection details, findings table, roof overview, annotated overview (orthomosaic with markers), anomaly detail sections, and recommended next steps.
- Template avoids fragile Word/Google Docs features such as text boxes and SmartArt.
- Placeholders are named consistently with `inspection.yaml`.
- Nate can restyle the template without changing renderer code.

### References

- `docs/research/Improved Template Mockup - Administrative Building.docx`
- `docs/product/mvp-spec.md`

---

## #4 Define and validate the inspection.yaml schema

- State: Open
- Milestone: Phase 1: MVP report generator
- Labels: engineering, mvp, phase-1
- Link: https://github.com/davidklan-png/TrueVector/issues/4

### Goal

Make `inspection.yaml` precise enough that report generation is deterministic and validation errors are useful. The schema is written by the app, not the user, but must be well-defined for the renderer to depend on.

### Acceptance criteria

- Required fields are documented.
- The sample file in `examples/administrative-building/inspection.yaml` validates.
- Duplicate anomaly IDs fail validation.
- Missing image paths fail validation or produce clear errors.
- Certification expiration can be checked against inspection date when present.

### References

- `docs/product/data-format.md`
- `docs/product/mvp-spec.md`

---

## #5 Build local web app and report generator

- State: Open
- Milestone: Phase 1: MVP report generator
- Labels: engineering, mvp, phase-1
- Link: https://github.com/davidklan-png/TrueVector/issues/5

### Goal

Create the core local web application: a Python server that serves a browser UI, manages inspection data, and generates `.docx` reports from `inspection.yaml`.

### How it works

The inspector runs one command (e.g. `truevector`) to start the local server, then works in Chrome. The app reads and writes `inspection.yaml` — the user never hand-edits it.

### Acceptance criteria

- One command starts the server and opens the app in the default browser.
- Inspection metadata form (client, property, date, conditions, technician, equipment) saves to `inspection.yaml`.
- Report generator loads `inspection.yaml`, validates it, and renders the MVP DOCX template.
- Generated report includes metadata, findings table, overview images, and anomaly detail blocks.
- Anomaly count and total anomalous area are computed from the anomaly list.
- Clear UI feedback on warnings and output path after generation.

### Notes

- Backend: Python with Flask or FastAPI.
- Frontend: HTML/CSS/vanilla JavaScript. No heavy framework required for MVP.
- Report rendering: `docxtpl`.
- See also issues #11 and #12 for the image markup UI components.

---

## #6 Add searchable PDF export and text-layer verification

- State: Open
- Milestone: Phase 1: MVP report generator
- Labels: engineering, mvp, phase-1
- Link: https://github.com/davidklan-png/TrueVector/issues/6

### Goal

When the generated DOCX is exported to PDF, verify that the result contains real searchable text.

### Acceptance criteria

- App can export PDF when the required local dependency (LibreOffice) is available.
- Failure to export PDF does not destroy the DOCX output.
- A text extraction check confirms expected words are searchable.
- The app UI explains what to do if text extraction fails.

### Context

The original reports looked visually fine but had broken text layers due to print-to-PDF. This should become a regression check.

---

## #7 Create complete Administrative Building sample fixture

- State: Open
- Milestone: Phase 1: MVP report generator
- Labels: docs, mvp, phase-1, template
- Link: https://github.com/davidklan-png/TrueVector/issues/7

### Goal

Turn the current sample YAML into a fixture that can actually exercise the report generator and image markup UI.

### Acceptance criteria

- Add representative visual, thermal, orthomosaic, nadiral thermal, and anomaly close-up images.
- Confirm sample values match the mockup or are clearly marked as placeholders.
- Generated report from this fixture can be reviewed by Nate.
- Fixture contains no client-sensitive material.

### References

- `examples/administrative-building/inspection.yaml`
- `docs/research/Improved Template Mockup - Administrative Building.docx`

---

## #8 Prove the MVP workflow on a large 25+ anomaly report

- State: Open
- Milestone: Phase 1: MVP report generator
- Labels: engineering, mvp, phase-1, product
- Link: https://github.com/davidklan-png/TrueVector/issues/8

### Goal

Verify the generated report remains navigable when anomaly count is high.

### Acceptance criteria

- Select one Hazel Park report with at least 25 anomalies.
- Create a structured sample inspection file for it.
- Generate the report from the MVP workflow.
- Confirm findings table, TOC, page references, and anomaly sections are navigable.
- Decide whether quadrant/section overview pages are required for MVP.

### Context

The report feedback identified large reports as the place where the current manual workflow breaks down most severely.

---

## #9 Invite Nate to the repository once his GitHub username is confirmed

- State: Open
- Milestone: Phase 0: Report hygiene
- Labels: product, question
- Link: https://github.com/davidklan-png/TrueVector/issues/9

### Goal

Add Nate as a collaborator so he can review docs, comment on issues, and eventually approve generated report changes.

### Needed decision

Confirm Nate's GitHub username and intended permission level.

- GitHub username: **nate-truevektor**

### Suggested permission

Start with Write access if Nate will edit docs and issues directly. Use Triage access if he should only manage issues and discussions without pushing code.

### Acceptance criteria

- Nate's GitHub username is recorded in this issue.
- Nate is invited to the private repo.
- Nate confirms he can access issues and docs.

---

## #10 Set up Python web server and inspection data persistence

- State: Open
- Milestone: Phase 1: MVP report generator
- Labels: engineering, mvp, phase-1

### Goal

Stand up the Python backend that serves the browser UI and handles reading/writing `inspection.yaml`.

### Acceptance criteria

- Flask or FastAPI server starts with one command and serves the app on localhost.
- API endpoints for reading and writing inspection metadata and anomaly list.
- `inspection.yaml` is written atomically (no partial saves that corrupt the file).
- Server handles opening an existing inspection folder or creating a new one.
- Basic error responses for missing files or invalid data.

### Notes

This is the foundation all other app features are built on. Complete before #11 and #12.

---

## #11 Build thermal image markup UI

- State: Open
- Milestone: Phase 1: MVP report generator
- Labels: engineering, mvp, phase-1

### Goal

Let the inspector draw polygon outlines on nadiral thermal images to mark anomalous areas, directly in the browser.

### Acceptance criteria

- Thermal image is displayed at a usable size in the browser.
- User can click to place polygon vertices; clicking the first point again closes the polygon.
- Each closed polygon is associated with an anomaly ID.
- Polygon coordinates are saved to `inspection.yaml`.
- Marked-up image (thermal image with polygon overlay rendered in) is exported for use in the report.
- A single thermal image can have polygons for more than one anomaly.

### Notes

Use the HTML Canvas API for drawing. No third-party annotation library required for MVP.

---

## #12 Build orthomosaic anomaly ID placement UI

- State: Open
- Milestone: Phase 1: MVP report generator
- Labels: engineering, mvp, phase-1

### Goal

Let the inspector place labeled anomaly ID markers on the orthomosaic to show where each anomaly is located on the roof.

### Acceptance criteria

- Orthomosaic image is displayed in the browser with zoom/pan support.
- Two-click placement: first click positions the marker, second click confirms.
- Each marker displays the anomaly ID (e.g. "01", "02").
- Marker positions are saved to `inspection.yaml`.
- The annotated orthomosaic (with all markers rendered in) is exported for use in the report.
- Markers can be repositioned or removed before generating the report.
