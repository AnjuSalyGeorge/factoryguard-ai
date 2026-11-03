
from src.simulator.conveyor import ConveyorMachine
from src.simulator.machine import get_reading


def show_status(machine, title):
    print(f"\n--- {title} ---")

    status = machine.get_status()

    for key, value in status.items():
        print(f"{key}: {value}")


def main():
    machine = ConveyorMachine()

    show_status(machine, "INITIAL STATE")

    machine.update_sensors(get_reading("normal"))
    show_status(machine, "NORMAL OPERATION")

    machine.advance_time(1)
    machine.update_sensors(get_reading("jam"))
    show_status(machine, "JAM DETECTED")

    print(
        "\nUnsafe restart:",
        machine.restart()
    )

    machine.acknowledge_fault()

    machine.advance_time(1)
    machine.update_sensors(get_reading("normal"))

    print(
        "Clear resolved fault:",
        machine.clear_fault()
    )

    show_status(machine, "READY FOR REVIEW")

    print(
        "\nOperator approval:",
        machine.approve_restart()
    )

    print(
        "Simulated restart:",
        machine.restart()
    )

    show_status(machine, "RECOVERY COMPLETE")

    print("\nEVENT HISTORY")

    for event in machine.events:
        print(
            event.simulation_time_s,
            event.event_type,
            event.message
        )


if __name__ == "__main__":
    main()
