
from src.simulator.conveyor import ConveyorMachine
from src.simulator.machine import get_reading


machine = ConveyorMachine()

# 1. A jam occurs.
machine.update_sensors(get_reading("jam"))

print("Fault detected:", machine.state.value)

# 2. Unsafe restart attempt.
print("Immediate restart:", machine.restart())

# 3. Operator acknowledges the fault.
print("Acknowledged:", machine.acknowledge_fault())

# 4. Fault cannot be cleared while still active.
print("Clear active fault:", machine.clear_fault())

# 5. Simulate the obstruction being removed.
machine.advance_time(1)
machine.update_sensors(get_reading("normal"))

# 6. Clear the latched fault.
print("Clear resolved fault:", machine.clear_fault())
print("State:", machine.state.value)

# 7. Restart still requires operator approval.
print("Restart without approval:", machine.restart())

# 8. Operator approves.
print("Approved:", machine.approve_restart())

# 9. Simulated restart.
print("Restart:", machine.restart())
print("Final state:", machine.state.value)
