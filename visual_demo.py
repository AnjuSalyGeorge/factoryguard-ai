
from src.simulator.conveyor import ConveyorMachine
from src.simulator.machine import get_reading
from src.simulator.visualization import draw_conveyor


machine = ConveyorMachine()

machine.update_sensors(get_reading("jam"))

draw_conveyor(
    machine,
    output_path="conveyor_fault.png"
)
