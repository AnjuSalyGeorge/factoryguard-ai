
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from src.simulator.conveyor import ConveyorState


def draw_conveyor(machine, output_path=None):
    fig, ax = plt.subplots(figsize=(10, 4))

    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.set_aspect("equal")
    ax.axis("off")

    # Conveyor belt
    belt = Rectangle(
        (1, 1.5),
        8,
        1,
        facecolor="#777777",
        edgecolor="black",
        linewidth=2
    )
    ax.add_patch(belt)

    # Conveyor rollers
    for x in range(2, 9):
        ax.add_patch(
            plt.Circle(
                (x, 2),
                0.12,
                color="#333333"
            )
        )

    # Simulated product
    product = Rectangle(
        (4, 1.7),
        0.8,
        0.6,
        facecolor="#3498db",
        edgecolor="black"
    )
    ax.add_patch(product)

    # Machine state indicator
    running = machine.state == ConveyorState.RUNNING

    status_color = "#27ae60" if running else "#e74c3c"

    ax.add_patch(
        plt.Circle(
            (8.7, 3.2),
            0.18,
            color=status_color
        )
    )

    ax.text(
        1,
        3.2,
        f"Machine: {machine.machine_id}",
        fontsize=12,
        fontweight="bold"
    )

    ax.text(
        1,
        2.8,
        f"State: {machine.state.value}",
        fontsize=11
    )

    ax.text(
        1,
        0.7,
        f"Active faults: {', '.join(machine.active_faults) or 'None'}",
        fontsize=10
    )

    ax.set_title(
        "FactoryGuard AI - Simulated Conveyor Workcell",
        fontsize=14
    )

    if output_path:
        fig.savefig(
            output_path,
            dpi=150,
            bbox_inches="tight"
        )

    plt.show()
    plt.close(fig)
