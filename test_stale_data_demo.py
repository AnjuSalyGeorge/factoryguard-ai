
from src.simulator.conveyor import ConveyorMachine
from src.simulator.machine import get_reading


machine = ConveyorMachine()

machine.update_sensors(get_reading("jam"))
machine.acknowledge_fault()

machine.advance_time(1)
machine.update_sensors(get_reading("normal"))

print("Clear fault:", machine.clear_fault())

# Advance time without receiving new sensor readings.
machine.advance_time(10)

print("Readings fresh:", machine.get_status()["readings_fresh"])
print("Approval:", machine.approve_restart())
print("Restart:", machine.restart())
