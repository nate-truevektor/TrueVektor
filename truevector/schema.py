"""
Pydantic models for inspection.yaml.

The app writes and reads this file — inspectors never edit it by hand.
All fields reflect docs/product/data-format.md plus the web app additions
(polygon_coords for thermal markup, orthomosaic_marker for map placement).
"""

from __future__ import annotations

from datetime import date as Date
from typing import List, Optional, Tuple

from pydantic import BaseModel, Field, model_validator


# ---------------------------------------------------------------------------
# Sub-models
# ---------------------------------------------------------------------------

class Client(BaseModel):
    name: str = Field(..., description="Client organisation name")


class Property(BaseModel):
    name: str = Field(..., description="Property / building name")
    address: str = Field(..., description="Street address")


class InspectionConditions(BaseModel):
    date: Date = Field(..., description="Date the inspection was performed (YYYY-MM-DD)")
    report_date: Date = Field(..., description="Date the report is issued (YYYY-MM-DD)")
    time_context: str = Field(..., description="Time of day context, e.g. 'at sunset'")
    ambient_f: float = Field(..., description="Ambient temperature in °F")
    rh_pct: float = Field(..., description="Relative humidity in %")
    wind_mph: float = Field(..., description="Wind speed in MPH")
    narrative: str = Field(..., description="Free-form findings narrative")


class Technician(BaseModel):
    name: str
    certification: str = Field(..., description="Certification level, e.g. 'Level II Thermographer'")
    cert_provider: Optional[str] = None
    cert_number: Optional[str] = None
    cert_expires: Optional[Date] = Field(
        None, description="Certification expiration date. Missing or expired triggers a warning."
    )
    email: str
    phone: str


class Equipment(BaseModel):
    name: str = Field(..., description="Drone / camera model name")
    detector: str = Field(..., description="Infrared detector spec string")
    temperature_range: str = Field(..., description="Thermal camera temperature range")


class OverviewImages(BaseModel):
    """Inspection-level images (not per-anomaly)."""
    aerial_visual: str = Field(..., description="Path to aerial visual image, relative to inspection folder")
    aerial_thermal: str = Field(..., description="Path to aerial thermal image, relative to inspection folder")
    overview_annotated: str = Field(..., description="Path to annotated overview image, relative to inspection folder")
    orthomosaic: Optional[str] = Field(
        None, description="Path to orthomosaic image (from 3rd-party software), relative to inspection folder"
    )


class OrthoMarker(BaseModel):
    """
    Normalised position (0.0–1.0) of an anomaly ID label on the orthomosaic.
    (0, 0) = top-left corner of the image.
    """
    x: float = Field(..., ge=0.0, le=1.0)
    y: float = Field(..., ge=0.0, le=1.0)


class Anomaly(BaseModel):
    id: str = Field(..., description="Zero-padded string ID, e.g. '01', '02'")
    location: str = Field(..., description="Plain-English location on the roof")
    area_sqft: float = Field(..., gt=0, description="Approximate anomalous area in square feet")
    severity: str = Field(..., description="e.g. 'moderate', 'severe'")
    observation: str = Field(..., description="What was observed thermally")
    recommendation: str = Field(..., description="Recommended follow-up action")
    image: str = Field(..., description="Path to close-up image, relative to inspection folder")

    # Set by the thermal image markup UI (issue #11)
    polygon_coords: Optional[List[Tuple[float, float]]] = Field(
        None,
        description=(
            "Polygon vertices marking this anomaly on a nadiral thermal image. "
            "Each point is (x, y) normalised to 0.0–1.0 relative to image dimensions."
        ),
    )

    # Set by the orthomosaic placement UI (issue #12)
    orthomosaic_marker: Optional[OrthoMarker] = Field(
        None,
        description="Normalised (x, y) position of this anomaly's ID label on the orthomosaic.",
    )


# ---------------------------------------------------------------------------
# Root model
# ---------------------------------------------------------------------------

class InspectionReport(BaseModel):
    """Root model — mirrors the top-level keys of inspection.yaml."""

    client: Client
    property: Property
    inspection: InspectionConditions
    technician: Technician
    equipment: Equipment
    images: OverviewImages
    anomalies: List[Anomaly] = Field(default_factory=list)

    @model_validator(mode="after")
    def anomaly_ids_unique(self) -> "InspectionReport":
        seen: set[str] = set()
        for anomaly in self.anomalies:
            if anomaly.id in seen:
                raise ValueError(f"Duplicate anomaly ID: '{anomaly.id}'")
            seen.add(anomaly.id)
        return self
