# Mind at Work: Mental Health in Tech Survey

A reproducible Python EDA and interactive Streamlit dashboard for the 2014 OSMI Mental Health in Tech Survey.

## Project contents

- `Mental_Health_in_Tech_EDA.ipynb`: executed EDA notebook with data-quality checks, univariate, bivariate, geographic, workplace-support, association, and text analysis.
- `app.py`: interactive Streamlit application with filters, five analysis tabs, CSV upload, and filtered-data download.
- `analysis_utils.py`: reusable cleaning, index, rate, and association functions.
- `data/survey.csv`: source dataset used by the project.
- `requirements.txt`: deployment dependencies.
- `.streamlit/config.toml`: app theme.

## Run locally

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Upload this project folder to a GitHub repository.
2. Sign in to Streamlit Community Cloud and select **Create app**.
3. Choose the repository, branch, and `app.py` as the entry point.
4. Select **Deploy**. No secrets are required.

## Index definition and limitations

The Workplace Mental Health Support Index averages 11 equally weighted survey responses covering benefits, care options, wellness resources, help-seeking information, anonymity, leave, perceived consequences, openness with coworkers/supervisors, parity with physical health, and observed negative consequences. Responses are mapped to 0, 0.5, or 1 (with ordered leave values), then scaled to 0–100.

This index measures perceived workplace support within this survey sample. It is not a validated clinical scale and must not be used to diagnose individuals. Results are descriptive, observational, self-reported, and based on a non-random 2014 sample.

