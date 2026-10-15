# CodeAlpha_DataRedundancyRemovalSystem

A Flask-based cloud-ready data validation system for the CodeAlpha Cloud Computing Internship **Task 1: Data Redundancy Removal System**.

## Features

- Detects exact duplicate data using SHA-256 hashes.
- Detects highly similar text using `difflib.SequenceMatcher`.
- Classifies new data as:
  - `unique`
  - `possible_duplicate`
  - `redundant`
- Blocks redundant records before insertion.
- Uses SQLite with a unique hash constraint as a second protection layer.
- REST API plus a clean browser dashboard.
- Automated tests with pytest.
- Includes Dockerfile and Procfile for cloud deployment.

## Project structure

```text
CodeAlpha_DataRedundancyRemovalSystem/
├── app.py
├── requirements.txt
├── Procfile
├── Dockerfile
├── README.md
├── .gitignore
├── templates/
│   └── index.html
├── static/
│   └── style.css
└── tests/
    └── test_app.py
```

## Run locally

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`.

## Test

```bash
pytest -q
```

## API examples

### Validate

```bash
curl -X POST http://127.0.0.1:5000/api/validate \
  -H "Content-Type: application/json" \
  -d "{\"content\":\"Hello cloud\"}"
```

### Add a unique record

```bash
curl -X POST http://127.0.0.1:5000/api/records \
  -H "Content-Type: application/json" \
  -d "{\"content\":\"Unique cloud record\"}"
```

## Cloud deployment

The app is designed for platforms that run Flask/Gunicorn containers or web services. Example command:

```bash
gunicorn app:app
```

For production, replace SQLite with a managed database such as PostgreSQL and configure persistent storage.

## Internship task mapping

| Requirement | Implementation |
|---|---|
| Identify redundant/false-positive data | Hash + similarity classification |
| Validate new data against existing data | `/api/validate` |
| Prevent duplicates | Validation + DB UNIQUE constraint |
| Append unique verified data | `/api/records` |
| Database accuracy/efficiency | Normalized text + indexed unique hash |

## Demo flow

1. Add `Alice lives in Delhi`.
2. Add the same sentence again with different spaces/case.
3. The second request is rejected as redundant.
4. Try a slightly changed sentence to see the similarity classification.

## Author

CodeAlpha Cloud Computing Internship project.
