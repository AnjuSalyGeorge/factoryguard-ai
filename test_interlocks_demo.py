
from src.simulator.conveyor import ConveyorMachine
from src.simulator.machine import get_reading


machine = ConveyorMachine()
machine.update_sensors(get_reading("normal"))

machine.activate_emergency_stop()

print("Emergency state:", machine.state.value)
print("Restart:", machine.restart())

machine.release_emergency_stop()

print("After E-stop release:", machine.state.value)
print("Restart:", machine.restart())

machine.set_guard_door(False)

print("Guard closed:", machine.guard_door_closed)
print("Restart:", machine.restart())

machine.set_guard_door(True)

print("Guard closed:", machine.guard_door_closed)
print("Restart:", machine.restart())
