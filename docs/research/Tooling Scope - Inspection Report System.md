# Inspection Report System — Scoping Doc

**Audience:** implementer (Beep or similar). Nate is the end user.
**Context:** True Vektor produces drone thermographic roof-inspection reports (currently Google Docs → print-to-PDF). Ten-report Hazel Park engagement reviewed June 2026; see companion feedback doc for the document-quality findings that motivate this.

## 1. Problem

The current workflow is entirely manual: images are cropped and placed into a gdocs template by hand, anomaly markers are drawn onto overview images by hand, and the per-anomaly knowledge in Nate's head (location, size, severity, what it probably is) never gets captured anywhere. At 2 anomalies per building that's tolerable; the same engagement had buildings with 25 and 40+ anomalies. The output PDF is also technically broken (no searchable text — print-driver artifact), and there's no structured data to roll up across an engagement or compare against a future re-scan.

## 2. Goals

1. Capture each anomaly as **structured data once**, at annotation time — location, geometry, area, severity, observation, recommendation.
2. **Generate the report automatically** from that data: cover with at-a-glance numbers, TOC when long enough, findings table, numbered overview, captioned per-anomaly pages, page numbers, and a *searchable* PDF.
3. Manage the surrounding objects: clients → properties → inspections → images.
4. Enable what manual workflows can't: engagement-level rollups and scan-over-scan comparison.

**Non-goals (v1):** multi-user/auth, cloud hosting, orthomosaic stitching, radiometric re-analysis, invoicing.

## 3. Phasing

### Phase 0 — Stop the bleeding (no code, this week)

- Export PDFs from gdocs (File → Download → PDF). Never print-to-PDF. This alone fixes search/copy/accessibility/indexing.
- Adopt the improved gdocs template (see companion mockup): cover block, findings table, captions, page numbers. Manual, but immediate.

### Phase 1 — Report generation CLI

One folder per inspection: `inspection.yaml` + images. A CLI renders the report.

```yaml
# inspection.yaml (sketch)
client: Hazel Park Schools
property:
  name: Hazel Park Administrative Building
  address: 123 Example Ave, Anytown, ST 00000
inspection:
  date: 2026-03-27
  technician: nate
  conditions: { ambient_f: 34, rh_pct: 54, wind_mph: 3 }
  equipment: dji-m2ea          # ref to equipment library
images:
  aerial_visual: visual.png
  aerial_thermal: thermal.png
  overview_annotated: overview.png   # Phase 1: pre-annotated; Phase 2: generated
anomalies:
  - id: 1
    location: East wing, east edge near parapet
    area_sqft: 10
    severity: moderate
    observation: Warm linear signature along membrane seam...
    recommendation: Core sample at marked reference ID...
    image: closeup-01.png
```

Rules engine in the renderer: include TOC if estimated pages > 8; findings table always; one detail block per anomaly; palette explanation block; footer with building + inspection date + page numbers; total area computed, not typed.

**Output: .docx** (so Nate can hand-edit in gdocs and export), optionally direct PDF for the no-edits case.

**Stack:** Python + `docxtpl` (Jinja2 inside a .docx template — Nate can restyle the template himself without touching code), or Node + `docx`. Recommend `docxtpl`: the template stays a Word/gdocs document, which keeps Nate in control of look-and-feel.

**Effort:** ~1–2 weekends including the template.

### Phase 2 — Annotation UI (the real win)

Local web app where Nate does the annotation work *and the structured data falls out as a byproduct*:

- Load the high-res thermal overview (and visual twin) for an inspection; pan/zoom.
- Draw a box/polygon on an anomaly → auto-assigned next ID → small form (location label, severity, observation, recommendation). Geometry stored.
- **Area auto-computed** from geometry × scale. Scale comes from user-entered GSD (ft/px) or two-point calibration against a known distance on the roof.
- **Close-up crops auto-generated** from each region (with padding + burned-in ID marker) — eliminates the manual screenshot/crop/place workflow entirely. Optionally pair the visual-spectrum crop of the same region, which the current reports lack.
- Overview image with numbered markers + legend **rendered, not hand-drawn**; auto-split into quadrant pages when anomaly count exceeds a threshold (~15).
- "Generate report" button → Phase 1 renderer.

**Stack:** FastAPI + SQLite backend; frontend with OpenSeadragon (deep-zoom for very large images; pre-tile with libvips) + Annotorious for the drawing layer. Plain JS or Svelte is plenty. Single-user, runs on Nate's machine (`pip install` / Docker / Tauri wrapper — implementer's choice).

**Effort:** ~2–4 weeks of part-time work for a usable v1.

### Phase 3 — Projects, rollups, history

- Entities: `Client → Property → Inspection → {Image, Anomaly}`, plus `Engagement` grouping inspections (the Hazel Park job is one engagement, ten inspections).
- **Engagement rollup report:** one table — building, anomaly count, anomalous SqFt, severity mix — almost certainly what the district's decision-maker actually wants, and currently doesn't exist.
- **Re-scan comparison:** overlay prior anomaly geometry on a new scan of the same property; report new/grown/resolved. This turns one-off inspections into a recurring monitoring product — a business upgrade, not just a tooling one.
- Library tables for boilerplate: technician profiles (with cert + expiration — surface a warning when expired; see feedback doc), equipment specs, standard text blocks.

**Effort:** incremental on Phase 2; rollup report is days, comparison is longer (registration/alignment between scans is the hard part — manual 2–4 point alignment is fine for v1).

## 4. Data model sketch

```
client(id, name, contact)
engagement(id, client_id, name, date_range)
property(id, client_id, name, address, roof_area_sqft?)
inspection(id, property_id, engagement_id, date, technician_id, ambient_f, rh_pct, wind_mph, equipment_id, narrative)
image(id, inspection_id, kind[aerial_visual|aerial_thermal|overview|closeup|other], path, gsd_ft_per_px?)
anomaly(id, inspection_id, seq_no, geometry_json, area_sqft, location_label, severity, observation, recommendation)
technician(id, name, cert_level, cert_no, cert_expires, email, phone)
equipment(id, name, detector, range)
```

SQLite. Images on disk, paths in DB. Everything exportable to the Phase 1 YAML so the renderer stays decoupled from the app.

## 5. Risks & open questions

- **Where do the high-res thermal overviews come from?** Single high-altitude frame, or stitched? If stitched, what does the stitching and what's the real GSD? This determines area-calculation accuracy. Either way, report areas as approximate (current reports already do).
- **Radiometric data.** The DJI M2EA writes R-JPEGs with per-pixel temperature data. If Nate keeps the originals, later versions could add real temperature scales, re-paletting, and delta-T callouts via the DJI Thermal SDK. Don't build on this for v1, but **don't let the originals get discarded**.
- **Image size in the browser.** Stitched orthos can be huge; deep-zoom tiling (libvips → DZI) solves it and OpenSeadragon consumes it natively.
- **Buy vs. build.** Commercial drone-roofing platforms exist in this space. Worth a half-day survey before Phase 2 — but they're subscription-priced, generic, and won't match a template Nate controls. Phases 0–1 are worth doing regardless.
- **Google Docs round-trip.** docxtpl output imports to gdocs cleanly if the template avoids exotic features (text boxes, SmartArt). Keep the template plain: headings, tables, inline images.

## 6. Recommended order

1. Phase 0 now — it's free and fixes the broken deliverable.
2. Phase 1 next — small, decoupled, immediately useful, and forces the data schema decisions cheaply.
3. Survey off-the-shelf options (half day), then commit to Phase 2.
4. Phase 3 rollup report as soon as Phase 2 data exists; re-scan comparison when a repeat client materializes.
