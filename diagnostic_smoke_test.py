
import json

from src.agents.diagnostic import DiagnosticAgent
from src.simulator.conveyor import ConveyorMachine
from src.simulator.machine import get_reading


machine = ConveyorMachine()
machine.update_sensors(get_reading("jam"))

vision_report = {
    "scene_status": "obstruction",
    "observations": [
        "An irregular object is visible on the belt"
    ],
    "suspected_issue": "Possible obstruction",
    "uncertainty": "Still image only",
}

documents = [
    {
        "id": "PROC-001",
        "title": "Conveyor Jam and Obstruction",
    }
]

agent = DiagnosticAgent()

report = agent.diagnose(
    machine_status=machine.get_status(),
    vision_report=vision_report,
    documents=documents,
)

print(json.dumps(report.to_dict(), indent=2))
