
from pathlib import Path
from PIL import Image, ImageDraw


OUTPUT_DIR = Path("data/scenarios")


def make_scene(scenario: str) -> Image.Image:
    if scenario not in {
        "normal",
        "misaligned",
        "obstruction",
    }:
        raise ValueError(f"Unknown scenario: {scenario}")

    image = Image.new("RGB", (800, 480), "#e8edf1")
    draw = ImageDraw.Draw(image)

    # Workcell floor and conveyor structure
    draw.rectangle(
        (55, 135, 745, 340),
        fill="#626f7b",
        outline="#263746",
        width=7,
    )

    # Conveyor belt
    draw.rectangle(
        (80, 165, 720, 310),
        fill="#9aa4ad",
        outline="#34424f",
        width=4,
    )

    # Guide rails
    draw.line(
        (80, 165, 720, 165),
        fill="#29343d",
        width=9,
    )
    draw.line(
        (80, 310, 720, 310),
        fill="#29343d",
        width=9,
    )

    # Roller lines
    for x in range(105, 710, 55):
        draw.line(
            (x, 173, x, 302),
            fill="#79838d",
            width=3,
        )

    # First normal component
    draw.rounded_rectangle(
        (165, 205, 255, 270),
        radius=6,
        fill="#2384bd",
        outline="#114f78",
        width=4,
    )

    if scenario == "normal":
        draw.rounded_rectangle(
            (405, 205, 495, 270),
            radius=6,
            fill="#2384bd",
            outline="#114f78",
            width=4,
        )

    elif scenario == "misaligned":
        # Rotated part near a fixed guide.
        part = Image.new("RGBA", (110, 80), (0, 0, 0, 0))
        pd = ImageDraw.Draw(part)
        pd.rounded_rectangle(
            (10, 10, 100, 70),
            radius=5,
            fill="#2384bd",
            outline="#114f78",
            width=4,
        )
        rotated = part.rotate(35, expand=True)
        image.paste(rotated, (445, 167), rotated)

        draw.rectangle(
            (570, 160, 588, 318),
            fill="#4b555e",
        )

    elif scenario == "obstruction":
        # Irregular foreign object on the belt.
        draw.polygon(
            [
                (440, 185),
                (490, 205),
                (515, 250),
                (472, 288),
                (418, 258),
                (425, 220),
            ],
            fill="#d68127",
            outline="#87430d",
            width=5,
        )

    # No fault-status text: the model must inspect
    # the visible objects rather than read an answer.
    return image


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for scenario in (
        "normal",
        "misaligned",
        "obstruction",
    ):
        path = OUTPUT_DIR / f"{scenario}.png"
        make_scene(scenario).save(path)
        print(f"Created: {path}")


if __name__ == "__main__":
    main()
