# End User Guide | NewsBot 2.0

## Choose the data source first

The homepage defaults to authentic historical BBC analytics, derived from 1,440 unique labeled articles in BBC News Train. The dashboard shows statistics only; it does not redistribute historical article bodies. Switch to **Synthetic demo** only when illustrating the separately stored 60 teaching records. The source selection changes the charts and CSV export, **not** the BBC classifier.

## Current BBC news

Use the **Current BBC News headlines** panel to select Top News, Technology, Business, World or Science. The official RSS feed supplies headlines with direct BBC links, and may be temporarily unreachable. These are not the historical labeled research articles. Click through to BBC News to read original content. Do not describe feed availability as guaranteed.

## Analyze an article

Paste an article of 30 to 30,000 characters. The category classifier uses real BBC trained coefficients. Sentiment, NER, extractive summary and statistical topic memberships are distinct signals. The topic model is trained on the synthetic teaching collection. For Spanish and French article text, the English trained classifier and VADER tone are outside validated domain and human review is required. Probability estimates are not calibrated certainty.

## Natural language queries

Ask `Show technology articles`, `How many sport articles?` or `Summarize business` to interrogate only the 60 synthetic demonstration entries. The chatbot has no licensed full text BBC archive. Use the RSS panel for current BBC titles and links.

## Multilingual lab

Paste English, Spanish or French input for language detection. Optional external translation requires an explicit checkbox acknowledging that the text will be sent to a third party service. Never paste confidential or sensitive material. The free hosted version offers LSA and TF IDF comparisons. Real neural MiniLM multilingual retrieval was executed in Google Colab and is not deployed to the Free Render service.

## Frequently asked questions

**Why not show all BBC articles?** The supplied corpus is used for historical research; public redistribution of original publisher article bodies requires appropriate rights. The public dashboard uses aggregate measurements.

**Are the current headlines from 2026?** The RSS panel queries BBC's live feed. The historical labeled BBC corpus has no verified publication dates.

**Do dashboard topics show emerging trends?** No. Topic words represent statistical clusters, and a time trend cannot be established for undated historical records.

**Does 96% accuracy mean current world news is reliable?** No. It is the held out accuracy on historic within corpus labels, not general current news or independent source validation.

**Is this a complete production system?** No. It is an educational research demonstration on a Free tier host, with known security, licensing and model performance limitations.

## Troubleshooting

A sleeping Render Free app may take time to respond. If the RSS panel reports a failure, use the official BBC News link. If multilingual translation fails, confirm consent, provider access and language selection. For missing NER in local setup install `en_core_web_sm`. The GitHub Actions workflow tests core endpoints and source identity. Do not run untrusted joblib or pickle artifacts.
