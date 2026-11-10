# NewsBot Intelligence System 2.0

ITAI 2373 Natural Language Processing Final Project | Idris Junaid

## Main project

[Open the NewsBot 2.0 Python backend, Flask frontend, tests and documentation](ITAI2373-NewsBot-Final/README.md).

The final project lives in `ITAI2373-NewsBot-Final/` and contains modular NLP analysis, a browser-based Flask dashboard, seven guided Jupyter notebooks, demonstration data and automated tests. It is an educational prototype, not an audited production system.

## Original midterm evidence

The root directory preserves the previously submitted `ITAI2373_NewsBot_Midterm (1).ipynb`, `MT_Technical_Report_IdrisJunaid_ITAI2373.pdf` and `MT_Reflective_Report_IdrisJunaid_ITAI2373.pdf`. The original midterm reported 96.53% held out accuracy on its BBC corpus. This result **does not apply** to the synthetic demonstration dataset used for final project smoke tests.

## Run and test

```bash
cd ITAI2373-NewsBot-Final
python -m pip install -r requirements.txt
python train.py --demo
python -m pytest -q
python app.py
```

Open http://127.0.0.1:5000 after starting the app. For meaningful evaluation replace the synthetic dataset with the instructor-approved BBC News Train CSV and train with `python train.py --csv "data/raw/BBC News Train.csv"`. Do not commit private or licensed data.

## Hosting

The repository includes a root `render.yaml` as an optional Render Blueprint. By default the demo hosting startup uses **synthetic sample data only**. A live hosted URL has not yet been established. Validate provenance and security before public hosting.

## Attribution and accountability

Source documents and portions of the implementation were prepared with AI assistance for student/team review. See `ITAI2373-NewsBot-Final/docs/individual_contributions.md`. Retain verified authorship and team attribution in all final submissions.
