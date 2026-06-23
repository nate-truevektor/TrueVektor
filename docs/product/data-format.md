# Inspection Data Format

The MVP source of truth is `inspection.yaml`.

```yaml
client:
  name: Hazel Park Schools

property:
  name: Hazel Park Administrative Building
  address: 123 Example Ave, Anytown, ST 00000

inspection:
  date: 2026-03-27
  report_date: 2026-06-08
  time_context: at sunset
  ambient_f: 34
  rh_pct: 54
  wind_mph: 3
  narrative: >
    Two anomalous areas totaling approximately 30 SqFt were identified,
    both on the east wing.

technician:
  name: Nate Klan
  certification: Level II Thermographer
  cert_provider: ITC
  cert_number: "REDACTED"
  cert_expires: null
  email: redacted@example.com
  phone: 000.000.0000

equipment:
  name: DJI Mavic 2 Enterprise Advanced
  detector: 640x512 infrared detector
  temperature_range: -40 C to 550 C

images:
  aerial_visual: images/aerial-visual.png
  aerial_thermal: images/aerial-thermal.png
  overview_annotated: images/overview-annotated.png

anomalies:
  - id: "01"
    location: East wing, east edge near parapet
    area_sqft: 10
    severity: moderate
    observation: >
      Warm linear signature along membrane seam; consistent with moisture
      tracking under membrane.
    recommendation: >
      Core sample or moisture meter verification at the marked reference ID.
    image: images/anomaly-01.png
```

## Notes

- Keep anomaly IDs as strings so report formatting can preserve `01`, `02`, etc.
- Store images on disk and reference paths from YAML.
- Treat all area values as approximate unless a calibrated measurement workflow exists.
- Preserve original thermal files even if the MVP only uses exported PNG/JPG images.
