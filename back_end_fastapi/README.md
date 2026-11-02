# Plant Pathology FastAPI backend

## Setup

```powershell
cd back_end_fastapi
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python download_dataset.py
uvicorn main:app --reload --port 8000
```

The prediction API starts immediately and reports whether no dataset has been indexed.
When the downloaded dataset is stored somewhere other than KaggleHub's default cache, set:

```powershell
$env:PLANT_DATASET_PATH="C:\path\to\dataset"
```

API documentation is available at `http://localhost:8000/docs`.
