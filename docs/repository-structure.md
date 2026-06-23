# Repository & Data Architecture

How TrueVector's work is split across a public code repository, a private product-documentation store, and shared Google Drive folders for client thermal data. This document defines what lives where, why, and the rules that keep client data out of public view.

## The core principle: separate by data sensitivity, not by convenience

Everything is placed according to one question — *who is allowed to see it.* Three tiers:

1. **Public GitHub repo** — the engine and the contract. Code, automation, schema, templates, and system documentation. Contains no client data, ever.
2. **Private product documentation** — the business knowledge. Positioning, pricing, client-facing standards, certifications, and research. Versioned, but never public.
3. **Google Drive** — the client data and binary assets. Per-inspection working folders with real YAML, thermal imagery, raw drone files, and generated reports.

The `inspection.yaml` file is the **contract** that connects all three: the public code knows how to read it, the private docs define what good content looks like, and the real instances live in Drive.

## Tier 1 — Public GitHub repo (code & automation collaboration)

This is the repo being transferred. It should hold only things safe for anyone on the internet to read.

```
TrueVector/                      (PUBLIC)
├── README.md
├── LICENSE                      (add one — public repos need an explicit license)
├── .gitignore
├── pyproject.toml               (or requirements.txt)
├── src/truevector/             code: CLI, validation, rendering, PDF export
│   ├── cli.py
│   ├── schema.py
│   ├── render.py
│   └── pdf_export.py
├── templates/                  .docx report template(s) — layout only, no client data
│   └── report-template.docx
├── schema/
│   └── inspection.schema.json  formal schema referenced by validation
├── examples/                   SYNTHETIC fixtures only (fake client/address/images)
│   └── sample-building/
│       ├── inspection.yaml
│       └── images/
├── docs/                       how the SYSTEM works (not the business)
│   ├── repository-structure.md (this file)
│   ├── data-format.md
│   ├── mvp-spec.md
│   ├── roadmap.md
│   ├── collaboration.md
│   └── Issues.md
├── tests/
└── .github/
```

Rule for this tier: if a file names a real client, address, person's contact info, certification number, or contains real thermal imagery, it does not belong here.

## Tier 2 — Private product documentation

Business and product knowledge that should stay private. Recommended home: a **separate private GitHub repo** (e.g. `truevector-product`), because these are text documents that benefit from version history and review — something Google Drive does poorly.

```
truevector-product/             (PRIVATE repo)
├── product/
│   ├── positioning.md
│   ├── pricing.md
│   ├── client-terminology.md   approved client-facing language
│   └── report-standards.md     what a finished report must contain
├── research/
│   ├── Report Feedback - True Vektor.docx
│   ├── Tooling Scope - Inspection Report System.md
│   └── Improved Template Mockup - Administrative Building.docx
├── credentials/
│   └── certifications.md        ITC cert numbers, providers, expirations
└── decisions/                   dated business/product decisions
```

Alternative if running a second repo is too much overhead: keep these in a private Google Drive folder instead. The tradeoff is losing diff/version history and pull-request review on written decisions. For a small two-person team this is acceptable, but the separate private repo is the cleaner long-term choice.

## Tier 3 — Google Drive (shared thermal docs & client data)

Drive is the right home for client inspection data because git handles large binaries (thermal imagery, raw radiometric/DJI files) poorly, and Nate already works in Drive and Word. Use one folder per inspection, named so it sorts and indexes cleanly.

```
TrueVector (Shared Drive)
├── 00-templates/               working templates Nate edits by hand
├── 01-clients/
│   └── <client-slug>/
│       └── <YYYY-MM-DD>-<property-slug>/   ONE inspection = ONE folder
│           ├── inspection.yaml             source of truth (real data)
│           ├── images/                     exported PNG/JPG used in the report
│           ├── raw/                        original radiometric / DJI files
│           └── generated/                  report.docx, report.pdf outputs
├── 02-delivered/               final signed PDFs sent to clients
└── 99-admin/                   cert scans, insurance, licensing
```

## The interface: how code (public) meets data (Drive)

The public CLI runs against a Drive-synced inspection folder. Nothing about client data enters the repo:

```
generate-report "~/Google Drive/TrueVector/01-clients/hazel-park/2026-03-27-admin-building/inspection.yaml"
```

The tool reads the YAML and its local `images/`, writes outputs to that folder's `generated/`. The repo only ever contains the **synthetic** `examples/sample-building/` fixture, which exists so the code can be tested and demoed without touching a real client.

## Naming conventions (worth fixing now)

- **Inspection folders:** `<YYYY-MM-DD>-<property-slug>` — date-first so they sort chronologically.
- **Client slugs:** lowercase, hyphenated, stable (e.g. `hazel-park-schools`).
- **Anomaly IDs:** zero-padded strings (`"01"`, `"02"`) — already the convention; keep it so report ordering and the future project database stay consistent.

These look like small details, but they are what lets Phase 2+ features (project database, engagement rollups, re-scan comparison) index Drive automatically instead of requiring a migration later.

## What goes where — quick reference

| Item | Public repo | Private docs | Google Drive |
|------|:-----------:|:------------:|:------------:|
| Renderer / CLI code | ✅ | | |
| Schema & validation | ✅ | | |
| Report template (layout) | ✅ | | |
| Synthetic sample fixture | ✅ | | |
| System/engineering docs | ✅ | | |
| Pricing, positioning, standards | | ✅ | |
| Research & feedback docs | | ✅ | |
| Certification records | | ✅ | |
| Real `inspection.yaml` | | | ✅ |
| Thermal imagery / raw drone files | | | ✅ |
| Generated & delivered reports | | | ✅ |

## Critical: scrub client data before the repo goes public

The repo as it stands today is **not safe to make public**. These files contain real client and personal data:

- `examples/administrative-building/inspection.yaml` — real client, address, Nate's cert number, email, phone.
- `docs/product/data-format.md` — same real data used as an example.
- `docs/research/*.docx` — client-specific feedback and mockups.

Two compounding risks: making the repo public exposes this immediately, and **git history is permanent** — deleting the files in a new commit does not remove them from history. Anyone can read prior commits.

Recommended sequence before completing the public transfer:

1. Move the research docs and any real data into the private Tier 2 location.
2. Replace `examples/administrative-building/` with a synthetic `examples/sample-building/` fixture (fake client, fake address, placeholder images). This also resolves issue #7's assumption that sample data was "approved for this private repo" — that approval no longer holds once public.
3. Rewrite the real data out of `data-format.md` using the synthetic values.
4. Purge the sensitive files from history with `git filter-repo` (or, simplest and safest, start the public repo from a fresh initial commit with clean content and no prior history).
5. Add a `LICENSE` so the public repo's terms of use are explicit.
6. Only then flip to public / finalize the transfer.

The cheapest path is usually #4's fresh-start option: the issue backlog is already preserved in `docs/Issues.md`, so a clean public repo loses nothing that matters while guaranteeing no client data is hiding in history.
