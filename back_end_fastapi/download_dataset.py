from pathlib import Path

import kagglehub


path = Path(kagglehub.dataset_download("sujallimje/plant-pathogens"))
print(f"Dataset downloaded to: {path}")
