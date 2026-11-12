
from app.dashboard_state import (
    new_dashboard_state,
    apply_scenario,
)


state = new_dashboard_state()

print("Initial machine state:")
print(state["machine"].get_status())

print("\nInjecting jam...")

status = apply_scenario(state, "jam")

print(status)

assert status["state"] == "STOPPED_FAULT"

print("\nSensor history records:")
print(len(state["sensor_history"]))

print("\nDashboard state test passed")
