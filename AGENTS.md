# AGENTS.md

Guidance for coding agents working in the TrueVektor repository.

## Project Context

TrueVektor is building a local inspection-report workflow for drone thermographic roof inspections. The MVP captures inspection metadata and anomaly findings once in `inspection.yaml`, validates that data, and uses it to generate an editable `.docx` report plus a searchable PDF.

Current repo state:

- Python package: `truevektor/`
- Data contract: `inspection.yaml`, modeled in `truevektor/schema.py`
- Validation entry point: `python -m truevektor.validator <inspection-folder>`
- Product docs: `docs/product/`
- Synthetic fixture location: `examples/`
- Issue templates: `.github/ISSUE_TEMPLATE/`

Keep the spelling consistent: the brand/repo is TrueVektor and the Python package is `truevektor`. Do not introduce `truevector` paths or commands.

## Primary Guardrail

This is a public repository. Never commit real client data.

Do not add:

- Real client names, addresses, emails, phone numbers, or certification numbers
- Real inspection YAML files
- Thermal imagery, raw drone files, orthomosaics, or generated client reports
- API keys, credentials, tokens, or machine-local secrets

Use only synthetic fixtures under `examples/`. Real inspection folders belong outside the repo, normally in a synced Google Drive folder with `inspection.yaml`, `images/`, `raw/`, and `generated/` subfolders.

## Recommended Target Structure

The repo is still early. Grow toward this structure as implementation begins:

```text
TrueVektor/
  AGENTS.md
  README.md
  LICENSE
  pyproject.toml
  .gitignore
  .github/
    ISSUE_TEMPLATE/
    workflows/
  docs/
    product/
      mvp-spec.md
      data-format.md
      roadmap.md
      collaboration.md
    engineering/
      architecture.md
      report-generation.md
    research/
  examples/
    sample-building/
      inspection.yaml
      images/
        README.md
  schema/
    inspection.schema.json
  templates/
    report-template.docx
  src/
    truevektor/
      __init__.py
      cli.py
      schema.py
      validator.py
      rendering/
        __init__.py
        docx_renderer.py
      export/
        __init__.py
        pdf_export.py
      web/
        __init__.py
        app.py
        static/
        templates/
  tests/
    fixtures/
    test_schema.py
    test_validator.py
    test_cli.py
```

Migration guidance:

- The current `truevektor/` package is acceptable while the repo is small.
- Move to `src/truevektor/` when adding `pyproject.toml`, CLI packaging, or tests that need installed-package behavior.
- Prefer `pyproject.toml` over expanding ad hoc scripts once dependencies include report generation, web UI, or test tooling.
- Keep `docs/product/` for product behavior and acceptance criteria. Put implementation notes in `docs/engineering/`.
- Keep generated reports out of git. If a generated artifact is needed for testing, use a tiny synthetic fixture and document why it is committed.

## Workflow For Agents

1. Read first: `README.md`, `docs/product/mvp-spec.md`, `docs/product/data-format.md`, and any issue or doc directly related to the task.
2. Confirm data sensitivity before editing examples, templates, or docs. If any value looks real, treat it as sensitive and ask before preserving it.
3. Make the smallest coherent change that advances the MVP. Avoid building Phase 2 features unless the task explicitly asks for them.
4. Keep `inspection.yaml` as the source of truth. Do not introduce hidden report state in generated files, UI-local storage, or sidecar formats unless documented and approved.
5. Validate schema changes against both docs and examples. Update `docs/product/data-format.md` when the YAML contract changes.
6. Add or update focused tests for schema, validation, rendering, CLI behavior, and PDF text-layer verification as those surfaces are implemented.
7. Keep public/private boundaries intact: code, schema, templates, tests, and synthetic examples in git; real inspection folders and generated client outputs outside git.
8. Before finishing, summarize changed files, commands run, and any tests that could not be run.

## Local Development Commands

Set up a local environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Validate the sample inspection folder:

```bash
python -m truevektor.validator examples/administrative-building
```

Expected caveat: validation currently requires referenced image files to exist. If the synthetic example does not include placeholder images, image-path validation will fail until those fixtures are added or the validator supports a schema-only mode.

## Implementation Priorities

Near-term recommendations from the current repo review:

1. Add packaging and test infrastructure: `pyproject.toml`, `pytest`, and CI under `.github/workflows/`.
2. Add `tests/` for duplicate anomaly IDs, missing required fields, missing image paths, and expired certification warnings.
3. Replace or rename `examples/administrative-building/` with a clearly synthetic `examples/sample-building/` fixture, including placeholder image files or documented image stubs.
4. Fix naming drift in comments and docs so commands always use `truevektor`.
5. Add a CLI module that wraps validation and later report generation, for example `truevektor.cli` with commands like `validate` and `generate-report`.
6. Add `templates/` only with client-neutral report layouts.
7. Add `schema/inspection.schema.json` only if it will be generated from, or kept in lockstep with, the Pydantic models.

## Report Generation Rules

- Generated `.docx` files must be editable and based on a template that avoids fragile layout constructs.
- PDF export must use a native export path, not print-to-PDF.
- PDF output must be verified to contain a searchable text layer.
- Zero-anomaly reports are valid.
- Large reports must remain navigable through the table of contents and findings table.

## Review Checklist

Before proposing or committing changes, check:

- No real client data or secrets were added.
- `inspection.yaml` examples still match `truevektor/schema.py`.
- Validator and CLI commands use `truevektor`, not `truevector`.
- Docs changed when behavior or data format changed.
- Tests were added or updated for behavior changes.
- Generated artifacts and local environment files remain ignored.
