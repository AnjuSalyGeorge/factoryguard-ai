
from src.rag.loader import (
    load_manuals,
    manual_to_text,
)


manuals = load_manuals()

print("Manuals loaded:", len(manuals))
print()

print(manual_to_text(manuals[0]))
