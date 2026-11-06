
from src.agents.evidence import assess_evidence


result = assess_evidence(
    sensor_faults=["OVERCURRENT", "LOW_RPM"],
    vision_status="normal",
)

print("Diagnosis:", result.diagnosis)
print("Severity:", result.severity)
print("Confidence:", result.confidence_label)
print("Limitations:", result.limitations)
