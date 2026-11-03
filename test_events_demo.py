
from src.simulator.conveyor import ConveyorMachine
from src.simulator.machine import get_reading


machine = ConveyorMachine()

machine.update_sensors(get_reading("jam"))
machine.restart()
machine.acknowledge_fault()

machine.advance_time(1)
machine.update_sensors(get_reading("normal"))

machine.clear_fault()
machine.approve_restart()
machine.restart()

print("\nFACTORYGUARD AI EVENT HISTORY")
print("-" * 65)

for event in machine.events:
    print(
        f"[{event.simulation_time_s:5.1f}s] "
        f"{event.event_type:22} "
        f"{event.message}"
    )
