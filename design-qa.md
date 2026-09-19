# Design QA

## Reference

Selected visual direction: Midnight Insight (option 2), desktop dashboard at 1440 x 1024.

## Implemented

- Deep navy layered background with violet, cyan, mint, and blue accents
- Branded header and restrained survey context
- Dark left-side filter rail with upload, country, gender, company-size, age, and reset controls
- Four responsive KPI cards
- Five functional analysis tabs
- Dark Plotly chart styling with accessible labels, restrained gridlines, and unified hover states
- Filtered data table and CSV download
- Responsive two-column and single-column breakpoints
- Descriptive, non-clinical index disclosure

## Functional verification

- Application loads with no Streamlit exceptions
- Five tabs detected
- Country, gender, company-size, and age filters detected
- Country filter change passed
- Reset Filters behavior passed
- Data explorer table loaded
- Treatment-driver selector loaded

## Visual verification

The local preview was blocked because the runtime attempted an unnecessary external IP lookup. No bypass was attempted. A browser screenshot of the actual Streamlit runtime could therefore not be captured in this environment.

**final result: blocked**

To complete visual QA, run the updated app locally and provide one full-page screenshot at approximately 1440 px width. Compare spacing, clipping, chart readability, sidebar proportions, and responsive behavior against the selected Midnight Insight reference.
