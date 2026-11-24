# NewsBot 2.0 Analytics and Reproducibility Upgrade

## Completed in source

* Responsive News Analytics dashboard with live calculations from the loaded model's data, including category breakdown and VADER sentiment breakdown.
* Both LDA and NMF topic model visualizations with assigned article counts and model derived keywords.
* Training holdout accuracy, macro F1, and cross validated comparison for the models already implemented in the project.
* Temporal distribution restricted to source provided dates.
* Downloadable aggregate CSV report without raw article text.
* BBC dataset preflight script with schema verification, class checks, and SHA256 fingerprint for reproducibility.
* Regression tests for the analytics endpoint, calculated totals, CSV export, and BBC shaped file structure.

## Not yet supported by evidence

* The authentic BBC training dataset has not been supplied to the workspace. Its final model scores cannot be calculated.
* The hosted site still runs on the explicitly synthetic 60 article teaching corpus. Its 50 percent held out demonstration accuracy is not a valid research performance result.
* No live news API or current events access has been added.
* Multilingual embedding retrieval and machine translation remain optional features and are not enabled by this change.
* Any additional score for an optional research extension must depend on actual implementation and validation, not this dashboard alone.

## Release checks

Review CI, `/health`, `/api/dashboard`, `/api/export/analytics.csv`, the topic method toggle, and the question and article analysis interfaces on the live site. Report merge commit and deployment ID with the individual portfolio documentation.
