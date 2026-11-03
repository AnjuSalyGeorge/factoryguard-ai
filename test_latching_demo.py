
from src.simulator.conveyor import ConveyorMachine
from src.simulator.machine import get_reading

machine = ConveyorMachine()

print("Initial state:", machine.state.value)

machine.update_sensors(get_reading("jam"))
print("After jam:", machine.state.value)
print("Fault latched:", machine.fault_latched)

machine.advance_time(1)
machine.update_sensors(get_reading("normal"))

print("After normal readings:", machine.state.value)
print("Fault latched:", machine.fault_latched)
print("Restart result:", machine.restart())
