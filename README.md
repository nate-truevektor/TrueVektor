# TrueVector Inspection Report System

Collaboration workspace for building TrueVector's drone thermographic roof-inspection report tooling.

## Product Goal

Reduce manual report production by capturing anomaly findings as structured data once, then generating a polished editable report and searchable PDF from that data.

## MVP

The MVP is a local report-generation workflow:

- one folder per inspection
- `inspection.yaml` as the source of truth
- source/overview/close-up images stored beside the YAML
- generated `.docx` report for review and hand edits
- searchable PDF export when no edits are needed

The annotation UI, auto-cropping, project database, engagement rollups, and re-scan comparison are intentionally after the MVP.

## Repository Map

- `docs/product/` - MVP spec, roadmap, data format, and collaboration process
- `docs/research/` - original review, scope, and template mockup documents
- `examples/` - sample inspection data shape for implementation
- `.github/ISSUE_TEMPLATE/` - issue forms for product, engineering, and documentation work

## Immediate Priorities

1. Use native PDF export, not print-to-PDF.
2. Update or remove the expired certification badge from report materials.
3. Finalize the improved report template.
4. Build a CLI that renders a `.docx` from `inspection.yaml`.
5. Prove the workflow on one small report and one large report.

## Working Agreement

Use GitHub Issues for product decisions and implementation tasks. Keep decisions in the relevant issue so report requirements do not live only in chat, email, or memory.
