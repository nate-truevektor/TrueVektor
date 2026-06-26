"""
TrueVektor report generator.

Generates a DOCX inspection report from inspection.yaml + settings.yaml.

Usage:
    from truevektor.report import generate_report
    out_path = generate_report(folder, settings)
"""

from __future__ import annotations

import io
import math
import tempfile
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def generate_report(folder: Path, settings: dict) -> Path:
    """
    Build a DOCX report for the inspection at `folder`.
    Returns the path to the written .docx file inside `folder`.
    """
    import yaml
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement

    # ── Load YAML ────────────────────────────────────────────────────────────
    with (folder / "inspection.yaml").open() as f:
        data = yaml.safe_load(f) or {}

    images_meta   = data.get("images") or {}
    inspection    = data.get("inspection") or {}
    client        = data.get("client") or {}
    property_d    = data.get("property") or {}
    tech          = data.get("technician") or {}
    equip_list    = data.get("equipment") or []
    all_anomalies = data.get("anomalies") or []

    # Only anomalies with polygon_coords appear in the report
    anomalies = [a for a in all_anomalies if a.get("polygon_coords")]

    company_name   = settings.get("company_name") or ""
    logo_path_str  = settings.get("logo_path") or ""
    logo_path      = Path(logo_path_str) if logo_path_str else None
    page2_sections = settings.get("page2_sections") or []

    report_date    = inspection.get("report_date") or inspection.get("date") or ""
    insp_date      = inspection.get("date") or ""

    # {total_area} substitution in narrative
    total_area = sum(float(a.get("area_sqft") or 0) for a in anomalies)
    narrative  = (inspection.get("narrative") or "").replace(
        "{total_area}", f"{total_area:,.0f}"
    )

    # ── Create document ───────────────────────────────────────────────────────
    doc = Document()

    # Page size: US Letter with 1" margins
    sec = doc.sections[0]
    sec.page_width      = Inches(8.5)
    sec.page_height     = Inches(11)
    sec.left_margin     = Inches(1.0)
    sec.right_margin    = Inches(1.0)
    sec.top_margin      = Inches(1.2)
    sec.bottom_margin   = Inches(1.0)
    sec.header_distance = Inches(0.4)
    sec.footer_distance = Inches(0.4)

    _set_header(sec, logo_path, doc)
    _set_footer(sec, company_name, report_date)

    # ── Cover page ────────────────────────────────────────────────────────────
    _add_cover(doc, company_name, client, property_d, insp_date, report_date)

    # ── Info / conditions page ────────────────────────────────────────────────
    doc.add_page_break()
    _add_info_page(doc, inspection, tech, equip_list, narrative)

    # ── Page-2 custom sections ────────────────────────────────────────────────
    for sec_def in page2_sections:
        heading = (sec_def.get("heading") or "").strip()
        body    = (sec_def.get("body") or "").strip()
        if heading:
            _add_section_heading(doc, heading)
        if body:
            doc.add_paragraph(body)

    # ── Aerial visual ─────────────────────────────────────────────────────────
    av_rel = images_meta.get("aerial_visual")
    if av_rel:
        av_path = folder / av_rel
        if av_path.is_file():
            doc.add_page_break()
            _add_section_heading(doc, "AERIAL OVERVIEW")
            _center_image(doc, av_path, Inches(6.0))

    # ── Orthomosaic with anomaly pins ─────────────────────────────────────────
    ortho_rel = images_meta.get("orthomosaic")
    if ortho_rel:
        ortho_path = folder / ortho_rel
        if ortho_path.is_file():
            doc.add_page_break()
            _add_section_heading(doc, "ORTHOMOSAIC — ANOMALY LOCATIONS")
            if anomalies:
                ortho_img = _composite_ortho(ortho_path, anomalies)
                buf = _pil_to_bytes(ortho_img)
                _center_image_from_bytes(doc, buf, Inches(6.0))
            else:
                _center_image(doc, ortho_path, Inches(6.0))

    # ── Anomaly detail pages (2 × 2 grid) ────────────────────────────────────
    if anomalies:
        doc.add_page_break()
        _add_section_heading(doc, "ANOMALY DETAILS")
        _add_anomaly_pages(doc, folder, anomalies)

    # ── Save ──────────────────────────────────────────────────────────────────
    out_path = folder / "inspection-report.docx"
    doc.save(str(out_path))
    return out_path


# ---------------------------------------------------------------------------
# Header / footer helpers
# ---------------------------------------------------------------------------

TITLE_TEXT = "Thermographic Scan Report"
GRAY = RGBColor(0x66, 0x66, 0x66)


def _set_header(section, logo_path: Optional[Path], doc) -> None:
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement

    header = section.header
    # Remove default empty paragraph
    for p in header.paragraphs:
        p._element.getparent().remove(p._element)

    # Two-column table: [logo] [title]
    tbl = header.add_table(rows=1, cols=2, width=Inches(6.5))
    tbl.style = "Table Grid"

    # Remove all borders from the table
    _remove_table_borders(tbl)

    left_cell  = tbl.cell(0, 0)
    right_cell = tbl.cell(0, 1)

    # Set column widths
    left_cell.width  = Inches(2.0)
    right_cell.width = Inches(4.5)

    # Logo in left cell
    lp = left_cell.paragraphs[0]
    lp.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = lp.add_run()
    if logo_path and logo_path.is_file() and logo_path.suffix.lower() in {
        ".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff", ".tif"
    }:
        try:
            run.add_picture(str(logo_path), height=Inches(0.45))
        except Exception:
            pass  # Logo unreadable — leave blank

    # Title in right cell
    rp = right_cell.paragraphs[0]
    rp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = rp.add_run(TITLE_TEXT)
    run.font.size  = Pt(10)
    run.font.color.rgb = GRAY
    run.font.bold  = False

    # Horizontal rule below header (bottom border on the last cell row)
    _add_horizontal_rule_after_table(tbl)


def _set_footer(section, company_name: str, report_date: str) -> None:
    from docx.shared import Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    footer = section.footer
    fp = footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    parts = []
    if company_name:
        parts.append(company_name)
    if report_date:
        parts.append(f"Report Date: {report_date}")
    text = " ■ ".join(parts) if parts else TITLE_TEXT
    run = fp.add_run(text)
    run.font.size      = Pt(9)
    run.font.color.rgb = GRAY


# ---------------------------------------------------------------------------
# Cover page
# ---------------------------------------------------------------------------

def _add_cover(doc, company_name, client, property_d, insp_date, report_date):
    from docx.shared import Pt, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    # Spacer
    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(48)

    # Main title
    tp = doc.add_paragraph()
    tp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = tp.add_run("THERMOGRAPHIC SCAN REPORT")
    run.font.size = Pt(22)
    run.font.bold = True

    if company_name:
        cp = doc.add_paragraph()
        cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = cp.add_run(company_name)
        run.font.size      = Pt(13)
        run.font.color.rgb = GRAY

    doc.add_paragraph()  # spacer

    # Details table
    rows = []
    if client.get("name"):
        rows.append(("Client", client["name"]))
    if property_d.get("name"):
        rows.append(("Property", property_d["name"]))
    if property_d.get("address"):
        rows.append(("Address", property_d["address"]))
    if insp_date:
        rows.append(("Inspection Date", insp_date))
    if report_date:
        rows.append(("Report Date", report_date))

    if rows:
        tbl = doc.add_table(rows=len(rows), cols=2)
        tbl.style = "Table Grid"
        _remove_table_borders(tbl)
        for i, (label, value) in enumerate(rows):
            lc = tbl.cell(i, 0)
            vc = tbl.cell(i, 1)
            lc.width = Inches(2.0)
            vc.width = Inches(4.5)
            lp = lc.paragraphs[0]
            run = lp.add_run(label)
            run.font.bold = True
            run.font.size = Pt(11)
            vp = vc.paragraphs[0]
            vp.add_run(value).font.size = Pt(11)


# ---------------------------------------------------------------------------
# Info page
# ---------------------------------------------------------------------------

def _add_info_page(doc, inspection, tech, equip_list, narrative):
    from docx.shared import Pt
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    # Inspection conditions
    _add_section_heading(doc, "INSPECTION CONDITIONS")
    cond_rows = [
        ("Date",        inspection.get("date") or ""),
        ("Time",        inspection.get("time_context") or ""),
        ("Temperature", f"{inspection.get('ambient_f') or ''}°F"),
        ("Humidity",    f"{inspection.get('rh_pct') or ''}%"),
        ("Wind",        f"{inspection.get('wind_mph') or ''} mph"),
    ]
    _add_kv_table(doc, [(k, v) for k, v in cond_rows if v.strip("°%  ")])

    # Technician
    _add_section_heading(doc, "TECHNICIAN")
    tech_rows = [
        ("Name",          tech.get("name") or ""),
        ("Certification", tech.get("certification") or ""),
        ("Email",         tech.get("email") or ""),
        ("Phone",         tech.get("phone") or ""),
    ]
    _add_kv_table(doc, [(k, v) for k, v in tech_rows if v])

    # Equipment
    if equip_list:
        _add_section_heading(doc, "EQUIPMENT")
        for eq in equip_list:
            name  = eq.get("name") or ""
            det   = eq.get("detector") or ""
            rng   = eq.get("temperature_range") or ""
            parts = [x for x in [name, det, rng] if x]
            if parts:
                doc.add_paragraph(
                    " — ".join(parts),
                    style="List Bullet"
                )

    # Narrative / findings
    if narrative:
        _add_section_heading(doc, "FINDINGS")
        for para_text in narrative.split("\n"):
            if para_text.strip():
                doc.add_paragraph(para_text.strip())


# ---------------------------------------------------------------------------
# Anomaly grid pages
# ---------------------------------------------------------------------------

def _add_anomaly_pages(doc, folder: Path, anomalies: list) -> None:
    from docx.shared import Inches, Pt
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    COLS = 2
    IMG_W = Inches(2.85)
    IMG_H = Inches(2.4)
    CELL_W = Inches(3.1)

    # Group into pages of 4
    pages = [anomalies[i:i + 4] for i in range(0, len(anomalies), 4)]

    for page_idx, page_anomalies in enumerate(pages):
        if page_idx > 0:
            doc.add_page_break()

        # Pad to 4 so we always have 2 rows
        padded = page_anomalies + [None] * (4 - len(page_anomalies))

        tbl = doc.add_table(rows=2, cols=COLS)
        tbl.style = "Table Grid"
        _remove_table_borders(tbl)

        for idx, anomaly in enumerate(padded):
            row_i = idx // COLS
            col_i = idx  % COLS
            cell  = tbl.cell(row_i, col_i)
            cell.width = CELL_W

            if anomaly is None:
                continue

            img_rel   = anomaly.get("image")
            poly_coords = anomaly.get("polygon_coords")
            anomaly_id  = anomaly.get("id") or str(idx + 1)
            location    = anomaly.get("location") or ""
            area        = anomaly.get("area_sqft") or ""
            observation = anomaly.get("observation") or ""
            severity    = anomaly.get("severity") or ""

            # Composited image
            img_bytes = None
            if img_rel:
                img_path = folder / img_rel
                if img_path.is_file():
                    try:
                        composited = _composite_anomaly(img_path, poly_coords)
                        img_bytes  = _pil_to_bytes(composited)
                    except Exception:
                        img_bytes = None
                    if img_bytes is None:
                        try:
                            img_bytes = img_path.read_bytes()
                            img_bytes = io.BytesIO(img_bytes)
                        except Exception:
                            img_bytes = None

            # Image paragraph
            ip = cell.paragraphs[0]
            ip.alignment = WD_ALIGN_PARAGRAPH.CENTER
            if img_bytes:
                try:
                    ip.add_run().add_picture(img_bytes, width=IMG_W)
                except Exception:
                    ip.add_run(f"[Image unavailable]")
            else:
                ip.add_run(f"[No image]")

            # Detail text
            def _detail(label, value, bold_label=True):
                dp = cell.add_paragraph()
                run_l = dp.add_run(f"{label}: ")
                run_l.font.bold = bold_label
                run_l.font.size = Pt(9)
                run_v = dp.add_run(str(value))
                run_v.font.size = Pt(9)
                dp.paragraph_format.space_before = Pt(2)
                dp.paragraph_format.space_after  = Pt(2)

            _detail("Anomaly", f"#{anomaly_id}")
            if location:
                _detail("Location", location)
            if area:
                _detail("Area", f"{float(area):,.0f} sq ft")
            if severity:
                _detail("Severity", severity)
            if observation:
                _detail("Observation", observation)


# ---------------------------------------------------------------------------
# Image compositing (Pillow)
# ---------------------------------------------------------------------------

def _composite_anomaly(img_path: Path, poly_coords) -> "Image":
    """Draw semi-transparent polygon overlay on a thermal image."""
    from PIL import Image, ImageDraw

    img = Image.open(img_path).convert("RGBA")
    w, h = img.size

    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw    = ImageDraw.Draw(overlay)

    if poly_coords and len(poly_coords) >= 3:
        pixels = [(float(x) * w, float(y) * h) for x, y in poly_coords]
        draw.polygon(pixels, fill=(255, 60, 60, 70))
        # Draw border (close the polygon)
        for i in range(len(pixels)):
            p1 = pixels[i]
            p2 = pixels[(i + 1) % len(pixels)]
            draw.line([p1, p2], fill=(255, 60, 60, 230), width=max(2, w // 200))

    composited = Image.alpha_composite(img, overlay).convert("RGB")
    return composited


def _composite_ortho(ortho_path: Path, anomalies: list) -> "Image":
    """Draw numbered circle pins on the orthomosaic for each anomaly."""
    from PIL import Image, ImageDraw, ImageFont

    img = Image.open(ortho_path).convert("RGBA")
    w, h = img.size

    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw    = ImageDraw.Draw(overlay)

    radius = max(12, min(w, h) // 60)
    font_size = max(10, radius)

    # Try to load a simple font; fall back to default
    font = None
    try:
        from PIL import ImageFont
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except Exception:
        pass  # use default bitmap font

    for anomaly in anomalies:
        marker = anomaly.get("orthomosaic_marker")
        if not marker:
            continue
        mx = float(marker.get("x") or 0) * w
        my = float(marker.get("y") or 0) * h
        label = str(anomaly.get("id") or "?")

        # Draw circle
        x0, y0 = mx - radius, my - radius
        x1, y1 = mx + radius, my + radius
        draw.ellipse([x0, y0, x1, y1], fill=(220, 40, 40, 230), outline=(255, 255, 255, 255))

        # Draw label
        if font:
            bbox = draw.textbbox((0, 0), label, font=font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        else:
            tw, th = font_size * len(label) * 0.6, font_size
        tx = mx - tw / 2
        ty = my - th / 2
        draw.text((tx, ty), label, fill=(255, 255, 255, 255), font=font)

    composited = Image.alpha_composite(img, overlay).convert("RGB")
    return composited


def _pil_to_bytes(img) -> "io.BytesIO":
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


# ---------------------------------------------------------------------------
# Document helpers
# ---------------------------------------------------------------------------

def _add_section_heading(doc, text: str) -> None:
    from docx.shared import Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after  = Pt(4)

    run = p.add_run(text)
    run.font.bold  = True
    run.font.size  = Pt(10)
    run.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
    run.font.all_caps  = True

    # Bottom border (rule)
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "4")
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), "AAAAAA")
    pBdr.append(bottom)
    pPr.append(pBdr)


def _add_kv_table(doc, rows: list) -> None:
    from docx.shared import Inches, Pt

    if not rows:
        return

    tbl = doc.add_table(rows=len(rows), cols=2)
    tbl.style = "Table Grid"
    _remove_table_borders(tbl)

    for i, (label, value) in enumerate(rows):
        lc = tbl.cell(i, 0)
        vc = tbl.cell(i, 1)
        lc.width = Inches(1.8)
        vc.width = Inches(4.7)

        run_l = lc.paragraphs[0].add_run(label)
        run_l.font.bold = True
        run_l.font.size = Pt(10)

        vc.paragraphs[0].add_run(value).font.size = Pt(10)


def _center_image(doc, img_path: Path, width) -> None:
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(img_path), width=width)


def _center_image_from_bytes(doc, buf, width) -> None:
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(buf, width=width)


def _remove_table_borders(tbl) -> None:
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement

    tbl_pr = tbl._tbl.get_or_add_tblPr()
    tbl_borders = OxmlElement("w:tblBorders")
    for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{side}")
        el.set(qn("w:val"), "none")
        tbl_borders.append(el)
    tbl_pr.append(tbl_borders)


def _add_horizontal_rule_after_table(tbl) -> None:
    """
    Add a thin gray line under a header table by adding a paragraph
    with a bottom border after the table inside the header.
    """
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    from docx.shared import Pt

    # Access the header body element and append a paragraph after the table
    tbl_el = tbl._tbl
    parent = tbl_el.getparent()

    rule_p = OxmlElement("w:p")
    pPr    = OxmlElement("w:pPr")
    pBdr   = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "4")
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), "CCCCCC")
    pBdr.append(bottom)

    # Tight spacing
    spacing = OxmlElement("w:spacing")
    spacing.set(qn("w:before"), "0")
    spacing.set(qn("w:after"), "0")
    pPr.append(spacing)
    pPr.append(pBdr)
    rule_p.append(pPr)

    # Insert after the table
    tbl_el.addnext(rule_p)
