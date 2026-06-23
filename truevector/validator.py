"""
Validate an inspection.yaml file.

Usage (CLI):
    python -m truevector.validator path/to/inspection/folder

Usage (programmatic):
    from truevector.validator import validate
    result = validate("path/to/inspection/folder")
    if not result.ok:
        print(result)
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from pydantic import ValidationError

from truevector.schema import InspectionReport


# ---------------------------------------------------------------------------
# Result container
# ---------------------------------------------------------------------------

@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0

    def __str__(self) -> str:
        lines: list[str] = []
        if self.ok:
            lines.append("✅  Validation passed")
        else:
            lines.append("❌  Validation failed")
        for e in self.errors:
            lines.append(f"   ERROR   {e}")
        for w in self.warnings:
            lines.append(f"   WARNING {w}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main validation function
# ---------------------------------------------------------------------------

def validate(folder: str | Path) -> ValidationResult:
    """
    Validate the inspection.yaml inside *folder*.

    Returns a ValidationResult with .ok, .errors, and .warnings.
    Never raises — all problems are captured in the result.
    """
    result = ValidationResult()
    folder = Path(folder).resolve()
    yaml_path = folder / "inspection.yaml"

    # 1. File must exist
    if not yaml_path.exists():
        result.errors.append(f"inspection.yaml not found in {folder}")
        return result

    # 2. Must be valid YAML
    try:
        with yaml_path.open() as f:
            raw = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        result.errors.append(f"YAML parse error: {exc}")
        return result

    if not isinstance(raw, dict):
        result.errors.append("inspection.yaml must be a YAML mapping (key: value pairs)")
        return result

    # 3. Schema validation via Pydantic (catches missing required fields,
    #    wrong types, and duplicate anomaly IDs via the model_validator)
    try:
        report = InspectionReport(**raw)
    except ValidationError as exc:
        for error in exc.errors():
            location = " → ".join(str(part) for part in error["loc"])
            result.errors.append(f"{location}: {error['msg']}")
        return result

    # 4. Image paths must exist on disk (relative to the inspection folder)
    image_fields = {
        "images.aerial_visual": report.images.aerial_visual,
        "images.aerial_thermal": report.images.aerial_thermal,
        "images.overview_annotated": report.images.overview_annotated,
    }
    if report.images.orthomosaic:
        image_fields["images.orthomosaic"] = report.images.orthomosaic

    for field_name, rel_path in image_fields.items():
        if not (folder / rel_path).exists():
            result.errors.append(f"Image not found — {field_name}: {rel_path}")

    for anomaly in report.anomalies:
        if not (folder / anomaly.image).exists():
            result.errors.append(
                f"Image not found — anomaly {anomaly.id}.image: {anomaly.image}"
            )

    # 5. Certification expiration — warning only, never an error
    tech = report.technician
    inspection_date = report.inspection.date

    if tech.cert_expires is None:
        result.warnings.append(
            "No certification expiration date on file for "
            f"{tech.name} ({tech.certification})"
        )
    elif tech.cert_expires < inspection_date:
        result.warnings.append(
            f"Certification expired {tech.cert_expires} — "
            f"before inspection date {inspection_date}. "
            "Verify credentials before issuing report."
        )

    return result


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python -m truevector.validator <inspection-folder>")
        sys.exit(1)

    result = validate(sys.argv[1])
    print(result)
    sys.exit(0 if result.ok else 1)


if __name__ == "__main__":
    main()
