
from src.simulator.machine import get_reading
from src.safety.controller import evaluate


def main():
    print("=" * 45)
    print("FACTORYGUARD AI")
    print("Industrial Fault Detection Demo")
    print("=" * 45)

    scenarios = [
        "normal",
        "jam",
        "overheating",
        "high_vibration",
    ]

    for scenario in scenarios:
        reading = get_reading(scenario)
        decision = evaluate(reading)

        print(f"\nScenario: {scenario.upper()}")
        print(f"Machine: {reading.machine_id}")
        print(f"Temperature: {reading.temperature_c} C")
        print(f"Current: {reading.current_a} A")
        print(f"Vibration: {reading.vibration_mm_s} mm/s")
        print(f"Motor RPM: {reading.rpm}")

        print(f"State: {decision.state.value}")

        if decision.faults:
            print("Detected faults:")
            for fault in decision.faults:
                print(f" - {fault}")
        else:
            print("Detected faults: None")

        print(
            "Restart permitted:",
            decision.restart_allowed,
        )


if __name__ == "__main__":
    main()
