# MVP Spec

## Scope

Build a local report-generation tool that converts structured inspection data and images into an editable `.docx` report. PDF export is useful, but `.docx` is the primary handoff because it lets Nate make final edits in Word or Google Docs.

## Non-Goals

- Multi-user accounts or auth.
- Cloud hosting.
- Annotation UI.
- Orthomosaic stitching.
- Radiometric image analysis.
- Invoicing or CRM features.
- Full client/property database.

## Inputs

Each inspection lives in one folder:

```text
inspection-folder/
  inspection.yaml
  images/
    aerial-visual.png
    aerial-thermal.png
    overview-annotated.png
    anomaly-01.png
    anomaly-02.png
```

The YAML file contains client, property, inspection, equipment, technician, image, and anomaly data.

## Output

The renderer produces:

- editable `.docx`
- optional searchable `.pdf`
- validation report in the terminal

## Required Report Sections

1. Cover
2. Optional table of contents for long reports
3. About this inspection
4. Inspection details
5. Summary of findings
6. Findings table
7. Roof overview
8. Annotated overview
9. Anomaly detail sections
10. Recommended next steps

## Required Anomaly Fields

- ID
- location on roof
- approximate area
- severity
- observation
- recommendation
- close-up image

## Validation Rules

The CLI should warn or fail clearly when:

- a required field is missing
- an image path does not exist
- anomaly IDs are duplicated or out of order
- total area in data conflicts with computed anomaly sum
- certification expiration is before the inspection date
- PDF export lacks searchable text

## Recommended Stack

Start with Python:

- `docxtpl` for template rendering
- `pydantic` or `jsonschema` for data validation
- `PyYAML` for YAML parsing
- LibreOffice or Word automation for PDF export where available

This keeps the template editable by non-developers and avoids building a UI before the data model is proven.
